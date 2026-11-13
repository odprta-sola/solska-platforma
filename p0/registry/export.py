"""Izvoz podatkov ene osebe za odgovor na zahtevo po dostopu (čl. 15) in prenosljivosti (čl. 20).

Izvoz vsebuje podatke, ki jih P0 hrani o osebi, in dejanja, ki jih je oseba izvedla kot
zaposleni. Podatkov drugih oseb ne razkriva, razen prikaznih imen oseb, s katerimi je povezana
(otroci, starši), in imen oddelkov. Imen zaposlenih, ki so spreminjali ali gledali podatke,
ne vsebuje (odločitev za DPO, D07); sklici na tuje entitete pri lastnih dejanjih so izpuščeni.
Gesla (tudi zgoščena) in seje niso del izvoza. Podatki M1/M2 niso v P0.
"""

from django.db.models import Q
from django.utils import timezone

from . import models as m

FORMAT = "odprta-sola/p0/izvoz-osebe/1"


def _t(value):
    return value.isoformat().replace("+00:00", "Z") if value else None


def _validity(obj):
    return {"velja_od": _t(obj.valid_from), "velja_do": _t(obj.valid_until)}


def _student_name(scope_key, names):
    return names.get(scope_key.split(":", 1)[1]) if scope_key.startswith("student:") else None


def changes_of(person, relationships, grants):
    """Sled sprememb osebe, njenih povezav in upravičenj.

    Številski ključi različnih modelov se lahko ujemajo, zato se filtrira po paru (vrsta, ID),
    nikoli samo po ID.
    """
    entities = {
        "person": [str(person.pk)],
        "relationship": [str(r.pk) for r in relationships],
        "grant": [str(g.pk) for g in grants],
    }
    match = Q()
    for entity_type, ids in entities.items():
        if ids:
            match |= Q(entity_type=entity_type, entity_id__in=ids)
    return m.ChangeAudit.objects.filter(match)


def person_export(person, now=None):
    """Slovar z vsemi podatki osebe v P0, pripravljen za JSON."""
    now = now or timezone.now()
    account = getattr(person, "account", None)
    student = getattr(person, "student", None)
    as_guardian = list(
        person.relationships.select_related("student__person").order_by("valid_from", "pk")
    )
    as_student = list(
        m.Relationship.objects.filter(student__person=person)
        .select_related("guardian")
        .order_by("valid_from", "pk")
    )
    grants = list(person.grants.select_related("approval").order_by("valid_from", "pk"))
    scope_refs = list(person.scope_refs.order_by("issued_at", "pk"))
    members = list(
        m.AudienceMember.objects.filter(person=person)
        .select_related("snapshot__school_class")
        .order_by("snapshot__created_at", "pk")
    )
    student_ids = {
        k.split(":", 1)[1]
        for k in [g.scope_key for g in grants]
        + [r.scope_key for r in scope_refs]
        + [x.scope_key for x in members]
        if k.startswith("student:")
    }
    names = {str(p.pk): p.display_name for p in m.Person.objects.filter(pk__in=student_ids)}
    return {
        "format": FORMAT,
        "izvozeno": _t(now),
        "oseba": {
            "id": str(person.pk),
            "prikazno_ime": person.display_name,
            "e_naslov": person.contact_email or None,
            "jezik": person.preferred_language,
            "ustvarjeno": _t(person.created_at),
            "vloge": sorted(r.role for r in person.roles.all()),
        },
        "izvorni_kljuci": [
            {"vir": s.source, "kljuc": s.source_key}
            for s in m.SourceMapping.objects.filter(
                entity_type="person", target_id=person.pk
            ).order_by("source", "source_key")
        ],
        "izvorni_kljuci_ucenca": [
            {"vir": s.source, "kljuc": s.source_key}
            for s in m.SourceMapping.objects.filter(
                entity_type="student", target_id=person.pk
            ).order_by("source", "source_key")
        ],
        "racun": None
        if account is None
        else {
            "uporabnisko_ime": account.username,
            "e_naslov": account.email or None,
            "aktiven": account.is_active,
            "ustvarjen": _t(account.date_joined),
            "zadnja_prijava": _t(account.last_login),
        },
        "oddelki_ucenca": []
        if student is None
        else [
            {"oddelek": str(x.school_class), **_validity(x)}
            for x in student.memberships.select_related("school_class").order_by("valid_from")
        ],
        "dodelitve_oddelkom": [
            {"oddelek": str(x.school_class), **_validity(x)}
            for x in person.staff_assignments.select_related("school_class").order_by("valid_from")
        ],
        "povezave_kot_stars": [
            {
                "ucenec": r.student.person.display_name,
                "vrsta": r.relationship_type,
                **_validity(r),
            }
            for r in as_guardian
        ],
        "povezave_kot_ucenec": [
            {"stars": r.guardian.display_name, "vrsta": r.relationship_type, **_validity(r)}
            for r in as_student
        ],
        "upravicenja": [
            {
                "ucenec": _student_name(g.scope_key, names),
                "dejanje": g.permission,
                **_validity(g),
                "potrditev": {"sklic": g.approval.reference, "cas": _t(g.approval.approved_at)},
            }
            for g in grants
        ],
        "sklici_na_obseg": [
            {
                "sklic": r.ref,
                "ucenec": _student_name(r.scope_key, names),
                "izdan": _t(r.issued_at),
                "poteče": _t(r.expires_at),
            }
            for r in scope_refs
        ],
        "obcinstva_kot_prejemnik": [
            {
                "namen": x.snapshot.purpose,
                "oddelek": str(x.snapshot.school_class),
                "ucenec": _student_name(x.scope_key, names),
                "ustvarjeno": _t(x.snapshot.created_at),
                "poteče": _t(x.snapshot.expires_at),
            }
            for x in members
        ],
        "spremembe_podatkov": [
            {
                "cas": _t(a.at),
                "dejanje": a.action,
                "vrsta": a.entity_type,
                "polja": a.changed_fields,
                "vir": a.source or None,
            }
            for a in changes_of(person, as_guardian + as_student, grants).order_by("at", "pk")
        ],
        "vpogledi_v_podatke": [
            {"cas": _t(a.at), "zaslon": a.screen}
            for a in m.AccessAudit.objects.filter(
                entity_type="person", entity_id=str(person.pk)
            ).order_by("at", "pk")
        ],
        "lastna_dejanja": {
            "spremembe": [
                {"cas": _t(a.at), "dejanje": a.action, "vrsta": a.entity_type, "vir": a.source}
                for a in m.ChangeAudit.objects.filter(actor=person).order_by("at", "pk")
            ],
            "vpogledi": [
                {"cas": _t(a.at), "zaslon": a.screen, "vrsta": a.entity_type}
                for a in m.AccessAudit.objects.filter(actor=person).order_by("at", "pk")
            ],
            "potrditve": [
                {"cas": _t(a.approved_at), "sklic": a.reference}
                for a in person.approvals.order_by("approved_at", "pk")
            ],
            "uvozi": [
                {"cas": _t(b.created_at), "vir": b.source, "stanje": b.status}
                for b in person.import_batches.order_by("created_at", "pk")
            ],
            "uveljavljeni_uvozi": [
                {"cas": _t(b.applied_at), "vir": b.source, "stanje": b.status}
                for b in person.applied_batches.order_by("applied_at", "pk")
            ],
            "obcinstva": [
                {
                    "namen": s.purpose,
                    "oddelek": str(s.school_class),
                    "ustvarjeno": _t(s.created_at),
                }
                for s in person.audiences.select_related("school_class").order_by(
                    "created_at", "pk"
                )
            ],
        },
    }
