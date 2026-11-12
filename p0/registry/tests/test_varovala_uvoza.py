"""Varovala uvoza: usklajenost z ročnim odvzemom in rok začasnih datotek (regresijski testi)."""

import json
import threading
import time
from datetime import timedelta
from unittest import mock

from django.core.management import call_command
from django.db import connection, connections, transaction
from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from registry import authz, importer, services, uploads
from registry import models as m

from .test_import import SRC, load
from .test_varovala import audience_of, contact_for, staff_session
from .test_zasloni import ScreenBase, csv_files

WAIT = 10  # zgornja meja čakanja na dogodke (s); test ob preseku pade


def shifted(person_key, names=("relationships", "grants"), rel_type=None):
    files = load()
    for name in names:
        out = []
        for line in files[name].decode().splitlines():
            if line.startswith(f"{person_key};"):
                parts = line.split(";")
                parts[3] = "2026-09-02T00:00:00Z"
                if rel_type and name == "relationships":
                    parts[2] = rel_type
                line = ";".join(parts)
            out.append(line)
        files[name] = ("\n".join(out) + "\n").encode()
    return files


def lock_waiters():
    """Število transakcij, ki čakajo na transakcijsko ključavnico (advisory) v PostgreSQL."""
    with connections["default"].cursor() as cursor:
        cursor.execute("SELECT count(*) FROM pg_locks WHERE locktype = 'advisory' AND NOT granted")
        return cursor.fetchone()[0]


def wait_for_waiter(timeout=WAIT):
    """Počaka, da druga transakcija čaka na ključavnico. Vrne False ob preseku (brez napake)."""
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if lock_waiters():
            return True
        time.sleep(0.02)
    return False


class Worker(threading.Thread):
    """Nit z lastno povezavo; izjema se shrani in test jo preveri."""

    def __init__(self, fn):
        super().__init__(daemon=True)
        self.fn, self.result, self.error = fn, None, None

    def run(self):
        try:
            self.result = self.fn()
        except Exception as exc:  # noqa: BLE001 - shrani za preverjanje v testu
            self.error = exc
        finally:
            connection.close()

    def finish(self, test):
        self.join(WAIT * 2)
        test.assertFalse(self.is_alive(), "nit se ni končala")
        if self.error:
            raise self.error
        return self.result


class ConcurrentRevocationTests(TransactionTestCase):
    def setUp(self):
        self.actor = m.Person.objects.create(display_name="Pooblaščeni")
        m.PersonRole.objects.create(person=self.actor, role=m.Role.OFFICE)
        files = load()
        batch, _ = importer.preview(files, SRC, self.actor)
        importer.apply_batch(batch, files, self.actor)
        self.p1 = self.person("parent-01")
        self.p2 = self.person("parent-02")
        self.scope1 = f"student:{self.person('student-01').pk}"
        self.scope2 = f"student:{self.person('student-02').pk}"
        self.rel = m.Relationship.objects.get(guardian=self.p2)
        self.grant_p1 = m.Grant.objects.get(person=self.p1, scope_key=self.scope1)

    def person(self, key):
        mp = m.SourceMapping.objects.get(source=SRC, entity_type="person", source_key=key)
        return m.Person.objects.get(pk=mp.target_id)

    def allowed(self, person, scope):
        return authz.check_grant(person, scope, "acknowledge")[0]

    def import_paused_at(self, files, entity, person, scope_key=None):
        """Uveljavitev, ki se ustavi takoj po branju odvzema za dani obseg."""
        reached, release = threading.Event(), threading.Event()
        original = importer._manual_revocation_at

        def instrumented(entity_type, model, scope):
            value = original(entity_type, model, scope)
            scope = scope or {}
            owner = scope.get("guardian") or scope.get("person")
            match = scope_key is None or scope.get("scope_key") == scope_key
            if entity_type == entity and owner == person and match and not reached.is_set():
                reached.set()
                release.wait(WAIT)
            return value

        batch, result = importer.preview(files, SRC, self.actor)
        self.assertTrue(result.clean, [p.as_dict() for p in result.problems])

        def run():
            with mock.patch.object(importer, "_manual_revocation_at", instrumented):
                return importer.apply_batch(batch, files, self.actor)

        return Worker(run), reached, release

    def run_import_then_revoke(self, files, entity, person, revoke, scope_key=None):
        """Uvoz prebere odvzem (ga še ni), nato poskus odvzema v drugi povezavi, nato commit."""
        imp, reached, release = self.import_paused_at(files, entity, person, scope_key)
        imp.start()
        self.assertTrue(reached.wait(WAIT), "uvoz ni dosegel branja odvzema")
        rev = Worker(revoke)
        rev.start()
        wait_for_waiter()  # s popravkom odvzem čaka na ključavnico uvoza
        release.set()
        batch, _ = imp.finish(self)
        rev.finish(self)
        return batch

    def run_revoke_then_import(self, files, revoke):
        """Odvzem je izveden, a še ne potrjen; uvoz se začne; nato commit odvzema."""
        done, release = threading.Event(), threading.Event()
        batch, result = importer.preview(files, SRC, self.actor)
        self.assertTrue(result.clean, [p.as_dict() for p in result.problems])

        def paused_revoke():
            with transaction.atomic():
                revoke()
                done.set()
                release.wait(WAIT)

        rev = Worker(paused_revoke)
        rev.start()
        self.assertTrue(done.wait(WAIT), "odvzem se ni izvedel")
        imp = Worker(lambda: importer.apply_batch(batch, files, self.actor))
        imp.start()
        wait_for_waiter()  # s popravkom uvoz čaka na ključavnico odvzema
        release.set()
        rev.finish(self)
        return imp.finish(self)

    def revoke_rel(self):
        authz.revoke_relationship(
            m.Relationship.objects.get(pk=self.rel.pk), actor=self.actor, source="rocno"
        )

    def revoke_grant_p1(self):
        authz.revoke_grant(
            m.Grant.objects.get(pk=self.grant_p1.pk), actor=self.actor, source="rocno"
        )

    def assert_scope_closed(self):
        self.assertFalse(self.allowed(self.p2, self.scope1))
        self.assertFalse(
            m.Relationship.objects.active().filter(guardian=self.p2).exists(),
            "v obsegu je ostala veljavna povezava",
        )
        self.assertTrue(
            m.ChangeAudit.objects.filter(action="relationship.revoked", source="rocno").exists()
        )
        self.assertTrue(self.allowed(self.p1, self.scope1))  # drug starš
        self.assertTrue(self.allowed(self.p1, self.scope2))  # drug otrok

    def test_uvoz_pred_odvzemom_povezave_premaknjen_zacetek(self):
        self.run_import_then_revoke(shifted("parent-02"), "relationship", self.p2, self.revoke_rel)
        self.assert_scope_closed()

    def test_uvoz_pred_odvzemom_povezave_druga_vrsta(self):
        files = shifted("parent-02", rel_type="guardian")
        self.run_import_then_revoke(files, "relationship", self.p2, self.revoke_rel)
        self.assert_scope_closed()

    def test_odvzem_povezave_pred_uvozom(self):
        batch, result = self.run_revoke_then_import(shifted("parent-02"), self.revoke_rel)
        self.assertEqual(batch.status, m.ImportBatch.Status.REJECTED)
        self.assertIn("manual_restriction", {p.code for p in result.problems})
        self.assert_scope_closed()

    def test_odvzem_povezave_pred_uvozom_druga_vrsta(self):
        files = shifted("parent-02", rel_type="guardian")
        batch, _ = self.run_revoke_then_import(files, self.revoke_rel)
        self.assertEqual(batch.status, m.ImportBatch.Status.REJECTED)
        self.assert_scope_closed()

    def test_uvoz_pred_odvzemom_granta(self):
        files = shifted("parent-01", names=("grants",))
        self.run_import_then_revoke(
            files, "grant", self.p1, self.revoke_grant_p1, scope_key=self.scope1
        )
        self.assertFalse(self.allowed(self.p1, self.scope1))
        self.assertTrue(self.allowed(self.p1, self.scope2))
        self.assertTrue(self.allowed(self.p2, self.scope1))

    def test_odvzem_granta_pred_uvozom(self):
        files = shifted("parent-01", names=("grants",))
        batch, _ = self.run_revoke_then_import(files, self.revoke_grant_p1)
        self.assertEqual(batch.status, m.ImportBatch.Status.REJECTED)
        self.assertFalse(self.allowed(self.p1, self.scope1))
        self.assertTrue(self.allowed(self.p1, self.scope2))

    def test_odvzem_iz_zastarelega_zaslona_po_uvozu(self):
        """Uvoz ustvari novo povezavo; odvzem izbere staro vrstico in mora zapreti obseg."""
        files = shifted("parent-02")
        batch, _ = importer.preview(files, SRC, self.actor)
        importer.apply_batch(batch, files, self.actor)
        self.assertTrue(self.allowed(self.p2, self.scope1))
        self.revoke_rel()
        self.assert_scope_closed()

    def test_odvzem_granta_iz_zastarelega_zaslona_po_uvozu(self):
        files = shifted("parent-01", names=("grants",))
        batch, _ = importer.preview(files, SRC, self.actor)
        importer.apply_batch(batch, files, self.actor)
        self.revoke_grant_p1()
        self.assertFalse(self.allowed(self.p1, self.scope1))
        self.assertTrue(self.allowed(self.p1, self.scope2))

    def test_druga_serija_po_odvzemu(self):
        self.run_import_then_revoke(shifted("parent-02"), "relationship", self.p2, self.revoke_rel)
        files = shifted("parent-02", rel_type="guardian")
        batch, result = importer.preview(files, SRC, self.actor)
        self.assertIn("manual_restriction", {p.code for p in result.problems})
        self.assert_scope_closed()

    def test_vse_stiri_poti_po_tekmi(self):
        staff = self.person("staff-01")
        author = staff_session(staff)
        before = audience_of(author, staff)  # posnetek pred tekmo
        _, token = services.create_service_client("m1", ["p0.contacts.resolve"])
        self.run_import_then_revoke(shifted("parent-02"), "relationship", self.p2, self.revoke_rel)
        account = m.Account.objects.create(username="p2-test", person=self.p2)
        client = Client()
        client.force_login(account)
        rels = client.get("/p0/api/v1/me/relationships").json()["relationships"]
        student1 = str(self.person("student-01").pk)
        self.assertFalse([r for r in rels if r["student_id"] == student1])
        ref = services.issue_scope_ref(self.p2, self.scope1)
        r = client.post(
            "/p0/api/v1/authorizations/check",
            data=json.dumps({"scope_ref": ref.ref, "permission": "m1.confirm"}),
            content_type="application/json",
        )
        self.assertEqual(r.json()["reason_code"], "NOT_ALLOWED")
        after = audience_of(author, staff)
        pairs = {(x["person_id"], x["student_label"]) for x in after["recipients"]}
        self.assertNotIn((str(self.p2.pk), "Učenec Testni 01"), pairs)
        self.assertEqual(contact_for(before, self.p2, token).status_code, 403)
        self.assertEqual(contact_for(before, self.p1, token).status_code, 200)


class UploadExpiryTests(ScreenBase):
    def preview(self):
        r = self.login().post("/p0/evidenca/uvoz/", {"source": "rok-test", "files": csv_files()})
        return m.ImportBatch.objects.get(pk=r["Location"].rstrip("/").split("/")[-1])

    def age(self, batch, hours):
        batch.uploads.update(created_at=timezone.now() - timedelta(hours=hours))

    def test_meja_roka(self):
        batch = self.preview()
        start = batch.uploads.order_by("created_at").first().created_at
        end = start + uploads.UPLOAD_RETENTION
        self.assertEqual(uploads.deadline(batch), end)
        self.assertFalse(uploads.expired(batch, end - timedelta(microseconds=1)))
        self.assertTrue(uploads.expired(batch, end))
        self.assertTrue(uploads.expired(batch, end + timedelta(seconds=1)))

    def test_ogled_ne_podaljsa_roka(self):
        batch = self.preview()
        before = list(batch.uploads.values_list("created_at", flat=True))
        self.client.get(f"/p0/evidenca/uvoz/{batch.pk}/")
        self.assertEqual(list(batch.uploads.values_list("created_at", flat=True)), before)

    def test_neposreden_ogled_po_izteku(self):
        batch = self.preview()
        self.age(batch, 25)
        r = self.client.get(f"/p0/evidenca/uvoz/{batch.pk}/")  # brez obiska začetne strani
        self.assertNotContains(r, "Uveljavi serijo")
        self.assertContains(r, "Naredite nov predogled")
        self.assertFalse(batch.uploads.exists())

    def test_neposredna_uveljavitev_po_izteku(self):
        batch = self.preview()
        self.age(batch, 25)
        r = self.client.post(f"/p0/evidenca/uvoz/{batch.pk}/uveljavi/", follow=True)
        self.assertContains(r, "Predogled je potekel")
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.PREVIEWED)
        self.assertFalse(batch.uploads.exists())
        self.assertFalse(m.SourceMapping.objects.filter(source="rok-test").exists())

    def test_pred_iztekom_se_uveljavi(self):
        batch = self.preview()
        self.age(batch, 23)
        self.client.post(f"/p0/evidenca/uvoz/{batch.pk}/uveljavi/")
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.APPLIED)

    def test_mesana_starost_ne_omogoci_delnega_uvoza(self):
        batch = self.preview()
        first = batch.uploads.order_by("pk").first()
        m.ImportUpload.objects.filter(pk=first.pk).update(
            created_at=timezone.now() - timedelta(hours=25)
        )
        self.client.post(f"/p0/evidenca/uvoz/{batch.pk}/uveljavi/")
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.PREVIEWED)
        self.assertFalse(m.SourceMapping.objects.filter(source="rok-test").exists())
        self.assertFalse(batch.uploads.exists())

    def test_iztek_med_branjem_in_zaklepom(self):
        """Rok se preveri v transakciji uveljavitve: pogled ga (kot ob tekmi) še ne vidi."""
        batch = self.preview()
        self.age(batch, 25)
        with mock.patch("registry.ui.uploads.expired", return_value=False):
            r = self.client.post(f"/p0/evidenca/uvoz/{batch.pk}/uveljavi/", follow=True)
        self.assertContains(r, "Predogled je potekel")
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.PREVIEWED)
        self.assertFalse(m.SourceMapping.objects.filter(source="rok-test").exists())


class UploadPurgeTests(TestCase):
    def setUp(self):
        self.batch_old = m.ImportBatch.objects.create(
            source="a", content_hash="x", status="previewed"
        )
        self.batch_new = m.ImportBatch.objects.create(
            source="b", content_hash="y", status="previewed"
        )
        now = timezone.now()
        m.ImportUpload.objects.create(
            batch=self.batch_old, name="persons", content=b"x", created_at=now - timedelta(hours=25)
        )
        m.ImportUpload.objects.create(
            batch=self.batch_old, name="roles", content=b"x", created_at=now - timedelta(hours=1)
        )
        m.ImportUpload.objects.create(
            batch=self.batch_new, name="persons", content=b"y", created_at=now
        )

    def test_ciscenje_brez_spletnih_zahtev_in_ponovljivo(self):
        call_command("purge_import_uploads", verbosity=0)
        self.assertFalse(self.batch_old.uploads.exists())  # cela serija, tudi novejša datoteka
        self.assertEqual(self.batch_new.uploads.count(), 1)
        call_command("purge_import_uploads", verbosity=0)
        self.assertEqual(self.batch_new.uploads.count(), 1)
        self.assertEqual(uploads.purge_expired(), 0)
