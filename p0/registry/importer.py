"""Uvoz CSV v evidenco P0 (docs/moduli/P0-uporabniki.md, razdelek »Predlog uvoznega formata«).

Pravila:
- Predogled in uveljavitev uporabljata isto kodo: predogled opravi vse spremembe v transakciji
  in jih prekliče. Kar predogled pokaže, bo uveljavitev tudi naredila.
- Uveljavitev je vse ali nič: napaka, konflikt ali izjema ne pusti delnih sprememb.
- Ponovni uvoz iste vsebine ne podvoji oseb (stabilna preslikava izvornih ključev).
- Manjkajoča vrstica nikoli ne izbriše osebe ali povezave in ne odvzame pravice.
- Starejši uvoz ne obnovi omejitve, ki jo je pooblaščena oseba ročno odvzela: to je konflikt.
- Uvoz ne spreminja gesel; gesla niso del uvoza.
"""

import csv
import hashlib
import io
from dataclasses import dataclass, field
from datetime import UTC, datetime

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.utils import timezone

from . import models as m

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_ROWS = 50_000

# Verzionirani šifranti; neznana vrednost je napaka.
PERMISSIONS = {"acknowledge", "decide"}
ROLES = {r.value for r in m.Role}
RELATIONSHIP_TYPES = {t.value for t in m.Relationship.Type}
STAFF_ROLES = {m.Role.TEACHER.value, m.Role.OFFICE.value}
IMPORTER_ROLES = {m.Role.OFFICE.value, m.Role.ADMIN.value}
# Vloge, ki jih sme z uvozom na novo dodeliti samo tehnični skrbnik (dajejo pravice uvoza
# ali skrbništva). Ponovni uvoz že dodeljene vloge je dovoljen.
ADMIN_ONLY_ROLES = {m.Role.ADMIN.value, m.Role.OFFICE.value}

# datoteka -> (obvezna polja, neobvezna polja, identiteta vrstice)
SCHEMA = {
    "classes": (["class_key", "name", "school_year"], [], ["class_key", "school_year"]),
    "persons": (["source_person_key", "display_name"], ["contact_email"], ["source_person_key"]),
    "roles": (["source_person_key", "role"], [], ["source_person_key", "role"]),
    "students": (
        ["source_student_key", "source_person_key"],
        [],
        ["source_student_key"],
    ),
    "memberships": (
        ["source_student_key", "class_key", "school_year", "valid_from"],
        ["valid_until"],
        ["source_student_key", "class_key", "valid_from"],
    ),
    "relationships": (
        ["source_person_key", "source_student_key", "relationship_type", "valid_from"],
        ["valid_until"],
        ["source_person_key", "source_student_key", "relationship_type", "valid_from"],
    ),
    "staff_assignments": (
        ["source_person_key", "class_key", "valid_from"],
        ["valid_until"],
        ["source_person_key", "class_key", "valid_from"],
    ),
    "grants": (
        ["source_person_key", "scope_key", "permission", "valid_from", "approval_ref"],
        ["valid_until"],
        ["source_person_key", "scope_key", "permission", "valid_from"],
    ),
}
ORDER = list(SCHEMA)  # vrstni red uveljavitve: reference najprej


@dataclass
class Problem:
    kind: str  # error | conflict
    file: str
    row: int
    code: str
    message: str

    def as_dict(self):
        return self.__dict__.copy()


@dataclass
class Op:
    entity_type: str
    key: str
    action: str
    changed_fields: list = field(default_factory=list)


@dataclass
class Result:
    problems: list
    ops: list
    content_hash: str

    @property
    def clean(self):
        return not self.problems

    @property
    def counts(self):
        counts = {}
        for op in self.ops:
            counts.setdefault(op.entity_type, {"create": 0, "update": 0, "unchanged": 0})
            counts[op.entity_type][op.action] += 1
        return counts


class Rollback(Exception):
    pass


def content_hash(files):
    h = hashlib.sha256()
    for name in sorted(files):
        h.update(name.encode())
        h.update(b"\0")
        h.update(hashlib.sha256(files[name]).digest())
    return h.hexdigest()


def _parse_date(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("manjka časovni pas")
    return dt.astimezone(UTC)


def parse_files(files, problems):
    """files: {ime_tabele: bajti}. Vrne {ime: [(številka vrstice, {polje: vrednost})]}."""
    tables = {}
    for name, raw in files.items():
        if name not in SCHEMA:
            problems.append(Problem("error", name, 0, "unknown_file", "Neznana datoteka."))
            continue
        if len(raw) > MAX_FILE_BYTES:
            problems.append(Problem("error", name, 0, "file_too_large", "Datoteka je prevelika."))
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            problems.append(Problem("error", name, 0, "bad_encoding", "Datoteka ni UTF-8."))
            continue
        required, optional, _ = SCHEMA[name]
        reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=";")
        header = reader.fieldnames or []
        missing = [c for c in required if c not in header]
        unknown = [c for c in header if c not in required + optional]
        if missing or unknown:
            problems.append(
                Problem(
                    "error",
                    name,
                    1,
                    "bad_header",
                    f"Manjkajoča polja: {missing}; neznana polja: {unknown}.",
                )
            )
            continue
        rows = []
        for i, raw_row in enumerate(reader, start=2):
            if len(rows) >= MAX_ROWS:
                problems.append(Problem("error", name, i, "too_many_rows", "Preveč vrstic."))
                break
            if None in raw_row or None in raw_row.values():
                problems.append(Problem("error", name, i, "bad_row", "Napačno število polj."))
                continue
            rows.append((i, {k: (v or "").strip() for k, v in raw_row.items()}))
        tables[name] = rows
    return tables


def validate_rows(tables, problems):
    """Preverjanja, ki ne potrebujejo evidence: obvezna polja, oblike, podvojeni ključi."""
    for name, rows in tables.items():
        required, _, identity = SCHEMA[name]
        seen = {}
        for i, row in rows:
            ok = True
            for col in required:
                if not row[col]:
                    problems.append(
                        Problem("error", name, i, "required_empty", f"Prazno polje {col}.")
                    )
                    ok = False
            if not ok:
                continue
            ident = tuple(row[c] for c in identity)
            if ident in seen:
                problems.append(
                    Problem(
                        "error",
                        name,
                        i,
                        "duplicate_key",
                        f"Podvojena vrstica (glej {seen[ident]}).",
                    )
                )
            seen[ident] = i
            for col in ("valid_from", "valid_until"):
                if row.get(col):
                    try:
                        row[col + "_parsed"] = _parse_date(row[col])
                    except ValueError:
                        problems.append(
                            Problem(
                                "error",
                                name,
                                i,
                                "bad_date",
                                f"{col}: potreben ISO 8601 s časovnim pasom.",
                            )
                        )
                        ok = False
            if (
                ok
                and row.get("valid_until_parsed")
                and row["valid_until_parsed"] <= row["valid_from_parsed"]
            ):
                problems.append(
                    Problem("error", name, i, "bad_range", "valid_until mora biti po valid_from.")
                )
            if row.get("contact_email"):
                try:
                    validate_email(row["contact_email"])
                except ValidationError:
                    problems.append(Problem("error", name, i, "bad_email", "Neveljaven e-naslov."))
            if name == "roles" and row["role"] not in ROLES:
                problems.append(Problem("error", name, i, "unknown_role", "Neznana vloga."))
            if name == "relationships" and row["relationship_type"] not in RELATIONSHIP_TYPES:
                problems.append(Problem("error", name, i, "unknown_type", "Neznan tip povezave."))
            if name == "grants":
                if row["permission"] not in PERMISSIONS:
                    problems.append(
                        Problem("error", name, i, "unknown_permission", "Neznano dovoljenje.")
                    )
                if not row["scope_key"].startswith("student:"):
                    problems.append(
                        Problem(
                            "error", name, i, "unknown_scope", "Podprt je obseg student:<ključ>."
                        )
                    )


def validate_references(tables, source, problems):
    """Reference morajo obstajati v uvozu ali v evidenci. Neznana referenca je napaka."""
    csv_persons = {r["source_person_key"] for _, r in tables.get("persons", [])}
    csv_students = {r["source_student_key"] for _, r in tables.get("students", [])}
    csv_classes = {(r["class_key"], r["school_year"]) for _, r in tables.get("classes", [])}
    db_persons = set(
        m.SourceMapping.objects.filter(source=source, entity_type="person").values_list(
            "source_key", flat=True
        )
    )
    db_students = set(
        m.SourceMapping.objects.filter(source=source, entity_type="student").values_list(
            "source_key", flat=True
        )
    )
    db_classes = set(m.SchoolClass.objects.values_list("class_key", "school_year"))
    persons, students, classes = (
        csv_persons | db_persons,
        csv_students | db_students,
        csv_classes | db_classes,
    )
    class_keys = {}
    for key, year in classes:
        class_keys.setdefault(key, set()).add(year)

    def role_of(key):
        roles = {r["role"] for _, r in tables.get("roles", []) if r["source_person_key"] == key}
        mp = m.SourceMapping.objects.filter(
            source=source, entity_type="person", source_key=key
        ).first()
        if mp:
            roles |= set(
                m.PersonRole.objects.filter(person_id=mp.target_id).values_list("role", flat=True)
            )
        return roles

    def need(ok, name, i, code, msg):
        if not ok:
            problems.append(Problem("error", name, i, code, msg))

    for i, r in tables.get("roles", []):
        need(r["source_person_key"] in persons, "roles", i, "unknown_person", "Neznana oseba.")
    for i, r in tables.get("students", []):
        need(r["source_person_key"] in persons, "students", i, "unknown_person", "Neznana oseba.")
    for i, r in tables.get("memberships", []):
        need(
            r["source_student_key"] in students,
            "memberships",
            i,
            "unknown_student",
            "Neznan učenec.",
        )
        need(
            (r["class_key"], r["school_year"]) in classes,
            "memberships",
            i,
            "unknown_class",
            "Neznan oddelek.",
        )
    for i, r in tables.get("relationships", []):
        need(
            r["source_person_key"] in persons,
            "relationships",
            i,
            "unknown_person",
            "Neznana oseba.",
        )
        need(
            r["source_student_key"] in students,
            "relationships",
            i,
            "unknown_student",
            "Neznan učenec.",
        )
    for i, r in tables.get("staff_assignments", []):
        need(
            r["source_person_key"] in persons,
            "staff_assignments",
            i,
            "unknown_person",
            "Neznana oseba.",
        )
        years = class_keys.get(r["class_key"], set())
        need(len(years) >= 1, "staff_assignments", i, "unknown_class", "Neznan oddelek.")
        need(
            len(years) <= 1,
            "staff_assignments",
            i,
            "ambiguous_class",
            "Oddelek ni enoličen med leti.",
        )
        if r["source_person_key"] in persons:
            need(
                bool(role_of(r["source_person_key"]) & STAFF_ROLES),
                "staff_assignments",
                i,
                "not_staff",
                "Dodelitev zahteva vlogo učitelja ali tajništva.",
            )
    for i, r in tables.get("grants", []):
        need(r["source_person_key"] in persons, "grants", i, "unknown_person", "Neznana oseba.")
        skey = r["scope_key"].split(":", 1)[1] if ":" in r["scope_key"] else ""
        need(skey in students, "grants", i, "unknown_student", "Obseg kaže na neznanega učenca.")
        has_rel = any(
            x["source_person_key"] == r["source_person_key"] and x["source_student_key"] == skey
            for _, x in tables.get("relationships", [])
        ) or _db_relationship_exists(source, r["source_person_key"], skey)
        need(has_rel, "grants", i, "grant_without_relationship", "Upravičenje zahteva povezavo.")


def _db_relationship_exists(source, person_key, student_key):
    pm = m.SourceMapping.objects.filter(
        source=source, entity_type="person", source_key=person_key
    ).first()
    sm = m.SourceMapping.objects.filter(
        source=source, entity_type="student", source_key=student_key
    ).first()
    return bool(
        pm
        and sm
        and m.Relationship.objects.filter(
            guardian_id=pm.target_id, student__person_id=sm.target_id
        ).exists()
    )


def _manually_revoked(entity_type, pk, source):
    return (
        m.ChangeAudit.objects.filter(
            action=f"{entity_type}.revoked", entity_type=entity_type, entity_id=str(pk)
        )
        .exclude(source__startswith="import:")
        .exists()
    )


def _manual_revocation_at(entity_type, model, scope):
    """Čas zadnjega ročnega odvzema v poslovnem obsegu (ne glede na vrstico uvoza) ali None."""
    if not scope:
        return None
    pks = [str(pk) for pk in model.objects.filter(**scope).values_list("pk", flat=True)]
    if not pks:
        return None
    audit = (
        m.ChangeAudit.objects.filter(
            action=f"{entity_type}.revoked", entity_type=entity_type, entity_id__in=pks
        )
        .exclude(source__startswith="import:")
        .order_by("-at")
        .first()
    )
    return audit.at if audit else None


def _stamp(obj, **fields):
    changed = []
    for name, value in fields.items():
        if getattr(obj, name) != value:
            setattr(obj, name, value)
            changed.append(name)
    return changed


class _Applier:
    def __init__(self, tables, source, actor, problems):
        self.t, self.source, self.actor, self.problems = tables, source, actor, problems
        self.ops = []
        self.audit_source = f"import:{source}"

    def person(self, key):
        mp = m.SourceMapping.objects.get(source=self.source, entity_type="person", source_key=key)
        return m.Person.objects.get(pk=mp.target_id)

    def student(self, key):
        mp = m.SourceMapping.objects.get(source=self.source, entity_type="student", source_key=key)
        return m.Student.objects.get(person_id=mp.target_id)

    def klass(self, key, year=None):
        qs = m.SchoolClass.objects.filter(class_key=key)
        return qs.get(school_year=year) if year else qs.get()

    def record(self, entity, key, action, changed, pk):
        self.ops.append(Op(entity, key, action, changed))
        if action != "unchanged":
            m.ChangeAudit.objects.create(
                actor=self.actor,
                action=f"{entity}.import_{action}d",
                entity_type=entity,
                entity_id=str(pk),
                source=self.audit_source,
                changed_fields=changed,
            )

    def conflict(self, name, i, entity, obj):
        self.problems.append(
            Problem(
                "conflict",
                name,
                i,
                "manual_restriction",
                "Zapis je bil ročno omejen; uvoz ga ne obnovi. Razreši pooblaščena oseba.",
            )
        )

    def upsert_validity(self, name, i, entity, key, model, lookup, row, extra=None, scope=None):
        """`scope` je poslovni obseg ročne omejitve (npr. skrbnik in učenec).

        Ročni odvzem v obsegu velja ne glede na začetek veljavnosti ali vrsto uvozne vrstice:
        uvoz ne sme ustvariti ali podaljšati zapisa, ki bi veljal po odvzemu.
        """
        until = row.get("valid_until_parsed")
        revoked_at = _manual_revocation_at(entity, model, scope)
        restores = revoked_at is not None and (until is None or until > revoked_at)
        obj = model.objects.filter(**lookup, valid_from=row["valid_from_parsed"]).first()
        if obj is None:
            if restores:
                self.conflict(name, i, entity, None)
                return None
            obj = model.objects.create(
                **lookup, valid_from=row["valid_from_parsed"], valid_until=until, **(extra or {})
            )
            self.record(entity, key, "create", ["*"], obj.pk)
            return obj
        extends = obj.valid_until is not None and (until is None or until > obj.valid_until)
        if extends and (restores or _manually_revoked(entity, obj.pk, self.source)):
            self.conflict(name, i, entity, obj)
            return obj
        changed = _stamp(obj, valid_until=until)
        if changed:
            obj.save(update_fields=changed)
        self.record(entity, key, "update" if changed else "unchanged", changed, obj.pk)
        return obj

    def run(self):
        for name in ORDER:
            for i, row in self.t.get(name, []):
                getattr(self, f"do_{name}")(name, i, row)

    def do_classes(self, name, i, row):
        key = f"{row['class_key']}/{row['school_year']}"
        obj = m.SchoolClass.objects.filter(
            class_key=row["class_key"], school_year=row["school_year"]
        ).first()
        if obj is None:
            obj = m.SchoolClass.objects.create(
                class_key=row["class_key"], school_year=row["school_year"], name=row["name"]
            )
            return self.record("class", key, "create", ["*"], obj.pk)
        changed = _stamp(obj, name=row["name"])
        if changed:
            obj.save(update_fields=changed)
        self.record("class", key, "update" if changed else "unchanged", changed, obj.pk)

    def do_persons(self, name, i, row):
        key = row["source_person_key"]
        mp = m.SourceMapping.objects.filter(
            source=self.source, entity_type="person", source_key=key
        ).first()
        if mp is None:
            person = m.Person.objects.create(
                display_name=row["display_name"], contact_email=row.get("contact_email", "")
            )
            m.SourceMapping.objects.create(
                source=self.source, entity_type="person", source_key=key, target_id=person.pk
            )
            return self.record("person", key, "create", ["*"], person.pk)
        person = m.Person.objects.get(pk=mp.target_id)
        changed = _stamp(
            person, display_name=row["display_name"], contact_email=row.get("contact_email", "")
        )
        if changed:
            person.save(update_fields=changed)
        self.record("person", key, "update" if changed else "unchanged", changed, person.pk)

    def do_roles(self, name, i, row):
        person = self.person(row["source_person_key"])
        _, created = m.PersonRole.objects.get_or_create(person=person, role=row["role"])
        self.record(
            "role",
            f"{row['source_person_key']}/{row['role']}",
            "create" if created else "unchanged",
            ["*"] if created else [],
            person.pk,
        )

    def do_students(self, name, i, row):
        person = self.person(row["source_person_key"])
        key = row["source_student_key"]
        existing = m.SourceMapping.objects.filter(
            source=self.source, entity_type="student", source_key=key
        ).first()
        if existing and existing.target_id != person.pk:
            self.problems.append(
                Problem(
                    "error", name, i, "key_remapped", "Ključ učenca je že vezan na drugo osebo."
                )
            )
            return
        _, created = m.Student.objects.get_or_create(person=person)
        if existing is None:
            m.SourceMapping.objects.create(
                source=self.source, entity_type="student", source_key=key, target_id=person.pk
            )
        self.record(
            "student",
            key,
            "create" if (created or existing is None) else "unchanged",
            ["*"] if (created or existing is None) else [],
            person.pk,
        )

    def do_memberships(self, name, i, row):
        student = self.student(row["source_student_key"])
        klass = self.klass(row["class_key"], row["school_year"])
        key = f"{row['source_student_key']}/{row['class_key']}"
        self.upsert_validity(
            name,
            i,
            "membership",
            key,
            m.Membership,
            {"student": student, "school_class": klass},
            row,
        )

    def do_relationships(self, name, i, row):
        guardian = self.person(row["source_person_key"])
        student = self.student(row["source_student_key"])
        key = f"{row['source_person_key']}/{row['source_student_key']}"
        self.upsert_validity(
            name,
            i,
            "relationship",
            key,
            m.Relationship,
            {
                "guardian": guardian,
                "student": student,
                "relationship_type": row["relationship_type"],
            },
            row,
            scope={"guardian": guardian, "student": student},
        )

    def do_staff_assignments(self, name, i, row):
        person = self.person(row["source_person_key"])
        klass = self.klass(row["class_key"])
        key = f"{row['source_person_key']}/{row['class_key']}"
        self.upsert_validity(
            name,
            i,
            "staff_assignment",
            key,
            m.StaffAssignment,
            {"person": person, "school_class": klass},
            row,
        )

    def do_grants(self, name, i, row):
        person = self.person(row["source_person_key"])
        skey = row["scope_key"].split(":", 1)[1]
        student = self.student(skey)
        relationship = (
            m.Relationship.objects.filter(guardian=person, student=student)
            .order_by("-valid_from")
            .first()
        )
        approval, _ = m.Approval.objects.get_or_create(
            reference=row["approval_ref"], defaults={"approved_by": self.actor}
        )
        key = f"{row['source_person_key']}/{row['scope_key']}/{row['permission']}"
        lookup = {
            "person": person,
            "scope_key": f"student:{student.person_id}",
            "permission": row["permission"],
        }
        self.upsert_validity(
            name,
            i,
            "grant",
            key,
            m.Grant,
            lookup,
            row,
            extra={"relationship": relationship, "approval": approval},
            scope=lookup,
        )


def _has_role(source, row):
    """Ali ima oseba iz vira vlogo iz vrstice že dodeljeno."""
    mp = m.SourceMapping.objects.filter(
        source=source, entity_type="person", source_key=row["source_person_key"]
    ).first()
    return (
        bool(mp) and m.PersonRole.objects.filter(person_id=mp.target_id, role=row["role"]).exists()
    )


def process(files, source, actor, apply=False):
    """Razčleni, validira in v transakciji izvede uvoz; uveljavi le pri `apply` in čisti seriji."""
    problems = []
    tables = parse_files(files, problems)
    chash = content_hash(files)
    if not tables and not problems:
        problems.append(Problem("error", "", 0, "empty", "Ni datotek za uvoz."))
    roles = set(actor.roles.values_list("role", flat=True)) if actor else set()
    if not roles & IMPORTER_ROLES:
        problems.append(
            Problem(
                "error", "", 0, "actor_not_authorized", "Uvoz sme izvesti tajništvo ali skrbnik."
            )
        )
    validate_rows(tables, problems)
    if m.Role.ADMIN.value not in roles:
        for i, r in tables.get("roles", []):
            if r["role"] in ADMIN_ONLY_ROLES and not _has_role(source, r):
                problems.append(
                    Problem(
                        "error",
                        "roles",
                        i,
                        "role_not_authorized",
                        "To vlogo sme dodeliti samo tehnični skrbnik.",
                    )
                )
    if problems:
        return Result(problems, [], chash)
    validate_references(tables, source, problems)
    if problems:
        return Result(problems, [], chash)

    ops = []
    try:
        with transaction.atomic():
            applier = _Applier(tables, source, actor, problems)
            applier.run()
            ops = applier.ops
            if problems or not apply:
                raise Rollback
    except Rollback:
        pass
    return Result(problems, ops, chash)


def _save_batch(source, actor, result, status):
    batch = m.ImportBatch.objects.create(
        source=source,
        created_by=actor,
        content_hash=result.content_hash,
        status=status,
        counts=result.counts,
        problems=[p.as_dict() for p in result.problems],
    )
    m.ImportPreview.objects.bulk_create(
        m.ImportPreview(
            batch=batch,
            entity_type=o.entity_type,
            source_key=o.key,
            action=o.action,
            changed_fields=o.changed_fields,
        )
        for o in result.ops
    )
    return batch


def preview(files, source, actor):
    result = process(files, source, actor, apply=False)
    status = m.ImportBatch.Status.PREVIEWED if result.clean else m.ImportBatch.Status.REJECTED
    return _save_batch(source, actor, result, status), result


def apply_batch(batch, files, actor):
    """Uveljavi prej pregledano serijo. Vsebina mora biti enaka tisti iz predogleda."""
    if batch.status != m.ImportBatch.Status.PREVIEWED:
        raise ValueError("Uveljaviti je mogoče samo čist predogled.")
    if batch.content_hash != content_hash(files):
        raise ValueError("Vsebina se razlikuje od predogleda.")
    try:
        result = process(files, batch.source, actor, apply=True)
    except Exception:
        batch.status = m.ImportBatch.Status.FAILED
        batch.save(update_fields=["status"])
        raise
    if not result.clean:
        batch.status = m.ImportBatch.Status.REJECTED
        batch.problems = [p.as_dict() for p in result.problems]
    else:
        batch.status = m.ImportBatch.Status.APPLIED
        batch.applied_at = timezone.now()
        batch.applied_by = actor
        batch.counts = result.counts
    batch.save()
    return batch, result
