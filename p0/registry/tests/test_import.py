from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from registry import authz, importer
from registry import models as m

DATA = Path(__file__).resolve().parents[3] / "data" / "testni-uvoz"
SRC = "test"


def load():
    return {p.stem: p.read_bytes() for p in DATA.glob("*.csv")}


def counts():
    return {
        model.__name__: model.objects.count()
        for model in (
            m.Person,
            m.Student,
            m.SchoolClass,
            m.Membership,
            m.Relationship,
            m.StaffAssignment,
            m.Grant,
            m.Approval,
            m.SourceMapping,
        )
    }


class ImportBase(TestCase):
    def setUp(self):
        self.actor = m.Person.objects.create(display_name="Pooblaščeni")
        m.PersonRole.objects.create(person=self.actor, role=m.Role.OFFICE)

    def apply(self, files=None):
        files = files if files is not None else load()
        batch, result = importer.preview(files, SRC, self.actor)
        self.assertTrue(result.clean, [p.as_dict() for p in result.problems])
        return importer.apply_batch(batch, files, self.actor)

    def errors(self, files):
        _, result = importer.preview(files, SRC, self.actor)
        return {p.code for p in result.problems}

    def key(self, entity, key):
        mp = m.SourceMapping.objects.get(source=SRC, entity_type=entity, source_key=key)
        return mp.target_id


class PreviewTests(ImportBase):
    def test_predogled_ne_spremeni_evidence(self):
        before = counts()
        batch, result = importer.preview(load(), SRC, self.actor)
        self.assertTrue(result.clean)
        self.assertEqual(counts(), before)
        self.assertEqual(batch.status, "previewed")
        self.assertEqual(result.counts["person"]["create"], 8)
        # predogled hrani imena polj, ne osebnih vrednosti
        self.assertFalse(any("Testni" in str(i.changed_fields) for i in batch.items.all()))

    def test_uveljavitev_ustvari_podatke(self):
        batch, _ = self.apply()
        self.assertEqual(batch.status, "applied")
        self.assertEqual(m.Person.objects.count(), 9)  # 8 + pooblaščeni
        self.assertEqual(m.Grant.objects.count(), 4)
        self.assertTrue(m.ChangeAudit.objects.filter(source=f"import:{SRC}").exists())

    def test_uvozeni_staros_deluje_z_avtorizacijo(self):
        self.apply()
        parent = m.Person.objects.get(pk=self.key("person", "parent-01"))
        scope = f"student:{self.key('student', 'student-01')}"
        self.assertEqual(authz.check_grant(parent, scope, "acknowledge"), (True, "ok"))
        other = f"student:{self.key('student', 'student-04')}"
        self.assertFalse(authz.check_grant(parent, other, "acknowledge")[0])


class IdempotencyTests(ImportBase):
    def test_ponovni_uvoz_ne_podvoji(self):
        self.apply()
        before = counts()
        batch, result = self.apply()
        self.assertEqual(counts(), before)
        self.assertTrue(all(o.action == "unchanged" for o in result.ops))

    def test_manjkajoca_vrstica_ne_odvzame_nicesar(self):
        self.apply()
        before = counts()
        files = load()
        files.pop("relationships")
        files.pop("grants")
        files["persons"] = (
            "source_person_key;display_name;contact_email\nparent-01;Starš Testni 01;\n".encode()
        )
        self.apply(files)
        after = counts()
        self.assertEqual(before, after)
        self.assertTrue(m.Relationship.objects.active().count() == 4)

    def test_sprememba_kontakta_je_sledljiva(self):
        self.apply()
        files = load()
        files["persons"] = files["persons"].replace(
            b"staff01@example.invalid", b"novi@example.invalid"
        )
        batch, result = self.apply(files)
        person = m.Person.objects.get(pk=self.key("person", "staff-01"))
        self.assertEqual(person.contact_email, "novi@example.invalid")
        self.assertTrue(
            m.ChangeAudit.objects.filter(
                action="person.import_updated",
                entity_id=str(person.pk),
                changed_fields=["contact_email"],
            ).exists()
        )

    def test_skupni_kontakt_ostane_dve_osebi(self):
        self.apply()
        a, b = self.key("person", "parent-01"), self.key("person", "parent-02")
        self.assertNotEqual(a, b)
        self.assertEqual(
            m.Person.objects.filter(contact_email="family01@example.invalid").count(), 2
        )


class ValidationTests(ImportBase):
    def test_napacen_csv_ne_spremeni_nicesar(self):
        files = load()
        files["relationships"] = (
            files["relationships"] + b"parent-01;student-99;parent;2026-09-01T00:00:00Z;\n"
        )
        before = counts()
        batch, result = importer.preview(files, SRC, self.actor)
        self.assertFalse(result.clean)
        self.assertEqual(batch.status, "rejected")
        self.assertEqual(counts(), before)
        self.assertIn("unknown_student", {p.code for p in result.problems})

    def test_posamezne_napake(self):
        base = load()
        cases = {
            "bad_date": ("memberships", b"2026-09-01T00:00:00Z;\n", b"01.09.2026;\n"),
            "bad_range": (
                "relationships",
                b"parent;2026-09-01T00:00:00Z;\n",
                b"parent;2026-09-01T00:00:00Z;2026-08-01T00:00:00Z\n",
            ),
            "unknown_role": ("roles", b"staff-01;teacher", b"staff-01;kralj"),
            "unknown_type": ("relationships", b";parent;", b";stric;"),
            "bad_email": ("persons", b"staff01@example.invalid", b"ni-naslov"),
            "unknown_permission": ("grants", b";acknowledge;", b";vse;"),
            "unknown_scope": ("grants", b"student:student-04", b"razred:razred-7a"),
        }
        for code, (name, old, new) in cases.items():
            files = dict(base)
            self.assertIn(old, files[name], code)
            files[name] = files[name].replace(old, new, 1)
            self.assertIn(code, self.errors(files), code)

    def test_podvojen_kljuc_in_prazno_polje(self):
        files = load()
        files["persons"] += b"parent-01;Drug;\n"
        self.assertIn("duplicate_key", self.errors(files))
        files = load()
        files["persons"] += b"parent-09;;\n"
        self.assertIn("required_empty", self.errors(files))

    def test_neznan_stolpec_in_datoteka(self):
        files = load()
        files["persons"] = b"source_person_key;display_name;geslo\nx;y;z\n"
        self.assertIn("bad_header", self.errors(files))
        self.assertIn("unknown_file", self.errors({**load(), "gesla": b"a;b\n"}))

    def test_upravicenje_brez_povezave(self):
        files = load()
        files.pop("relationships")
        self.assertIn("grant_without_relationship", self.errors(files))

    def test_dodelitev_zahteva_zaposlenega(self):
        files = load()
        files["staff_assignments"] = files["staff_assignments"].replace(b"staff-01", b"parent-01")
        self.assertIn("not_staff", self.errors(files))

    def test_uvoznik_mora_biti_pooblascen(self):
        m.PersonRole.objects.filter(person=self.actor).delete()
        m.PersonRole.objects.create(person=self.actor, role=m.Role.PARENT)
        self.assertIn("actor_not_authorized", self.errors(load()))

    def test_vsebina_ni_ut8(self):
        files = load()
        files["persons"] = b"\xff\xfe"
        self.assertIn("bad_encoding", self.errors(files))


class AtomicityTests(ImportBase):
    def test_izjema_med_uveljavitvijo_vrne_vse(self):
        files = load()
        batch, _ = importer.preview(files, SRC, self.actor)
        before = counts()
        original = importer._Applier.do_grants

        def boom(self, *a, **k):
            raise RuntimeError("izpad")

        importer._Applier.do_grants = boom
        try:
            with self.assertRaises(RuntimeError):
                importer.apply_batch(batch, files, self.actor)
        finally:
            importer._Applier.do_grants = original
        self.assertEqual(counts(), before)
        batch.refresh_from_db()
        self.assertEqual(batch.status, "failed")

    def test_uveljavitev_zahteva_isto_vsebino(self):
        files = load()
        batch, _ = importer.preview(files, SRC, self.actor)
        files["persons"] += b"parent-77;Nov;\n"
        with self.assertRaises(ValueError):
            importer.apply_batch(batch, files, self.actor)

    def test_zavrnjene_serije_ni_mogoce_uveljaviti(self):
        files = load()
        files["roles"] = files["roles"].replace(b"teacher", b"kralj")
        batch, _ = importer.preview(files, SRC, self.actor)
        with self.assertRaises(ValueError):
            importer.apply_batch(batch, files, self.actor)


class ManualRestrictionTests(ImportBase):
    def test_starejsi_uvoz_ne_obnovi_rocne_omejitve(self):
        self.apply()
        rel = m.Relationship.objects.get(guardian_id=self.key("person", "parent-02"))
        authz.revoke_relationship(rel, actor=self.actor, source="rocno")
        batch, result = importer.preview(load(), SRC, self.actor)
        self.assertFalse(result.clean)
        self.assertIn("manual_restriction", {p.code for p in result.problems})
        with self.assertRaises(ValueError):
            importer.apply_batch(batch, load(), self.actor)
        rel.refresh_from_db()
        self.assertIsNotNone(rel.valid_until)  # omejitev ostane

    def test_uvozni_zakljucek_ni_rocna_omejitev(self):
        self.apply()
        files = load()
        files["relationships"] = files["relationships"].replace(
            b"parent-02;student-01;parent;2026-09-01T00:00:00Z;",
            b"parent-02;student-01;parent;2026-09-01T00:00:00Z;2026-12-01T00:00:00Z",
        )
        self.apply(files)
        self.apply(load())  # uvoz sam je zaključil; nov uvoz ga sme znova odpreti
        rel = m.Relationship.objects.get(guardian_id=self.key("person", "parent-02"))
        self.assertIsNone(rel.valid_until)


class CommandTests(ImportBase):
    def test_ukaz_predogled_in_uveljavitev(self):
        m.Account.objects.create(username="tajnistvo", person=self.actor)
        call_command("import_csv", str(DATA), "--source", SRC, "--actor", "tajnistvo", verbosity=0)
        self.assertEqual(m.Grant.objects.count(), 0)
        batch = m.ImportBatch.objects.get()
        call_command(
            "import_csv",
            str(DATA),
            "--source",
            SRC,
            "--actor",
            "tajnistvo",
            "--apply-batch",
            str(batch.pk),
            verbosity=0,
        )
        self.assertEqual(m.Grant.objects.count(), 4)

    def test_ukaz_zavrne_neznanega_pooblascenca(self):
        with self.assertRaises(CommandError):
            call_command("import_csv", str(DATA), "--source", SRC, "--actor", "ni-ga", verbosity=0)
