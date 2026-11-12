"""Zasloni evidence: dostop, delovanje, sled in osnovna dostopnost (obseg T, točka 9)."""

from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase
from django.utils import timezone

from registry import authz
from registry import models as m

from .test_dostopnost import Page
from .test_import import DATA

BASE = "/p0/evidenca"


def person_of(key):
    mp = m.SourceMapping.objects.get(source_key=key, entity_type="person")
    return m.Person.objects.get(pk=mp.target_id)


def csv_files(**override):
    files = []
    for path in sorted(DATA.glob("*.csv")):
        content = override.get(path.stem, path.read_bytes())
        files.append(SimpleUploadedFile(path.name, content, content_type="text/csv"))
    return files


class ScreenBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_test_data", verbosity=0)
        cls.office = person_of("staff-03")
        cls.p1, cls.p2 = person_of("parent-01"), person_of("parent-02")

    def login(self, username="staff-03", client=None):
        client = client or self.client
        client.force_login(m.Account.objects.get(username=username))
        return client

    def urls(self):
        rel = m.Relationship.objects.filter(guardian=self.p1).first()
        grant = m.Grant.objects.filter(person=self.p1).first()
        return [
            f"{BASE}/osebe/",
            f"{BASE}/osebe/{self.p1.pk}/",
            f"{BASE}/osebe/{self.p1.pk}/kontakt/",
            f"{BASE}/osebe/{self.p1.pk}/povezave/{rel.pk}/odvzem/",
            f"{BASE}/osebe/{self.p1.pk}/upravicenja/{grant.pk}/odvzem/",
            f"{BASE}/uvoz/",
        ]

    def assert_accessible(self, response):
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        p = Page(response.content.decode())
        self.assertEqual(p.all("html")[0].get("lang"), "sl")
        self.assertEqual(len(p.all("h1")), 1)
        self.assertEqual(len(p.all("main")), 1)
        for field in p.inputs():
            if field.get("type") not in ("submit", "hidden"):
                self.assertIn(field.get("id"), p.labels_for, field)
        for th in p.all("th"):
            self.assertIn(th.get("scope"), ("col", "row"))
        for a in p.tags:
            ref = a[1].get("aria-describedby")
            for target in (ref or "").split():
                self.assertIn(target, p.ids)
        return p


class AccessTests(ScreenBase):
    def test_neprijavljen_preusmerjen_na_prijavo(self):
        for url in self.urls():
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302, url)
            self.assertTrue(r["Location"].startswith("/accounts/login/"), url)

    def test_stars_in_ucitelj_nimata_dostopa(self):
        for username in ("parent-01", "staff-01"):
            client = self.login(username, Client())
            for url in self.urls():
                r = client.get(url)
                self.assertEqual(r.status_code, 403, (username, url))
                self.assertContains(r, "Ni dostopa", status_code=403)
            self.assertEqual(client.post(f"{BASE}/uvoz/").status_code, 403)

    def test_tajnistvo_in_skrbnik_imata_dostop(self):
        m.PersonRole.objects.create(person=self.p2, role=m.Role.ADMIN)
        for username in ("staff-03", "parent-02"):
            client = self.login(username, Client())
            for url in self.urls():
                self.assertEqual(client.get(url).status_code, 200, (username, url))

    def test_obrazci_zahtevajo_csrf(self):
        client = self.login(client=Client(enforce_csrf_checks=True))
        rel = m.Relationship.objects.filter(guardian=self.p1).first()
        r = client.post(f"{BASE}/osebe/{self.p1.pk}/povezave/{rel.pk}/odvzem/")
        self.assertEqual(r.status_code, 403)
        rel.refresh_from_db()
        self.assertIsNone(rel.valid_until)

    def test_zacetna_stran_po_prijavi(self):
        r = self.login().get("/p0/")
        self.assertContains(r, "Uvoz CSV")
        r = self.login("parent-01", Client()).get("/p0/")
        self.assertNotContains(r, "Uvoz CSV")
        self.assert_accessible(r)

    def test_navigacija_samo_za_tajnistvo(self):
        self.assertNotContains(self.login("parent-01", Client()).get("/p0/"), f"{BASE}/osebe/")
        self.assertContains(self.login().get("/p0/"), f"{BASE}/osebe/")


class PersonScreenTests(ScreenBase):
    def test_seznam_iskanje_in_ubezanje(self):
        m.Person.objects.create(display_name="<script>alert(1)</script> Testna")
        client = self.login()
        r = client.get(f"{BASE}/osebe/", {"q": "Testna"})
        self.assert_accessible(r)
        html = r.content.decode()
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)
        r = client.get(f"{BASE}/osebe/", {"q": "Starš Testni 03"})
        self.assertContains(r, "Starš Testni 03")
        self.assertNotContains(r, "Starš Testni 01")

    def test_ostranjevanje(self):
        m.Person.objects.bulk_create(m.Person(display_name=f"Oseba {i:03}") for i in range(60))
        r = self.login().get(f"{BASE}/osebe/", {"stran": 2})
        self.assertContains(r, "Stran 2 od 2")

    def test_podrobnosti_osebe(self):
        r = self.login().get(f"{BASE}/osebe/{self.p1.pk}/")
        self.assert_accessible(r)
        self.assertContains(r, "Učenec Testni 01")
        self.assertContains(r, "Odvzemi povezavo")
        self.assertContains(r, "seznanitev (M1)")

    def test_neznana_oseba_404(self):
        r = self.login().get(f"{BASE}/osebe/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(r.status_code, 404)


class RevokeScreenTests(ScreenBase):
    def scope(self, student_key):
        return f"student:{person_of(student_key).pk}"

    def test_odvzem_povezave_s_potrditvijo_in_sledjo(self):
        client = self.login()
        rel = m.Relationship.objects.get(guardian=self.p2)
        url = f"{BASE}/osebe/{self.p2.pk}/povezave/{rel.pk}/odvzem/"
        r = client.get(url)
        self.assert_accessible(r)
        rel.refresh_from_db()
        self.assertIsNone(rel.valid_until)  # GET ne odvzame
        r = client.post(url)
        self.assertRedirects(r, f"{BASE}/osebe/{self.p2.pk}/", fetch_redirect_response=False)
        self.assertContains(client.get(r["Location"]), "Odvzem je izveden")
        self.assertFalse(authz.check_grant(self.p2, self.scope("student-01"), "acknowledge")[0])
        audit = m.ChangeAudit.objects.get(action="relationship.revoked", entity_id=str(rel.pk))
        self.assertEqual((audit.actor, audit.source), (self.office, "zaslon"))
        self.assertEqual(client.post(url).status_code, 404)  # že odvzeta
        r = client.get(f"{BASE}/osebe/{self.p2.pk}/")
        self.assertContains(r, "ne velja: povezava je zaključena")
        self.assertNotContains(r, "<td>veljavno</td>")

    def test_odvzem_upravicenja_ne_vpliva_na_drugega(self):
        client = self.login()
        grant = m.Grant.objects.get(person=self.p1, scope_key=self.scope("student-01"))
        client.post(f"{BASE}/osebe/{self.p1.pk}/upravicenja/{grant.pk}/odvzem/")
        self.assertFalse(authz.check_grant(self.p1, self.scope("student-01"), "acknowledge")[0])
        self.assertTrue(authz.check_grant(self.p1, self.scope("student-02"), "acknowledge")[0])
        self.assertTrue(
            m.ChangeAudit.objects.filter(action="grant.revoked", source="zaslon").exists()
        )

    def test_zapis_druge_osebe_ni_dosegljiv(self):
        rel = m.Relationship.objects.get(guardian=self.p2)
        r = self.login().post(f"{BASE}/osebe/{self.p1.pk}/povezave/{rel.pk}/odvzem/")
        self.assertEqual(r.status_code, 404)
        rel.refresh_from_db()
        self.assertIsNone(rel.valid_until)


class ContactScreenTests(ScreenBase):
    def url(self):
        return f"{BASE}/osebe/{self.p1.pk}/kontakt/"

    def test_neveljaven_naslov_z_dostopno_napako(self):
        r = self.login().post(self.url(), {"contact_email": "ni-naslov"})
        self.assertEqual(r.status_code, 200)
        p = self.assert_accessible(r)
        self.assertEqual(len([a for t, a in p.tags if a.get("role") == "alert"]), 1)
        field = next(a for a in p.inputs() if a.get("id") == "id_contact_email")
        self.assertEqual(field.get("aria-invalid"), "true")
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.contact_email, "family01@example.invalid")

    def test_sprememba_ima_sled_brez_vrednosti(self):
        r = self.login().post(self.url(), {"contact_email": "nova01@example.invalid"})
        self.assertRedirects(r, f"{BASE}/osebe/{self.p1.pk}/")
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.contact_email, "nova01@example.invalid")
        audit = m.ChangeAudit.objects.get(action="person.contact_updated")
        self.assertEqual(audit.changed_fields, ["contact_email"])
        self.assertEqual(audit.actor, self.office)
        self.assertNotIn("nova01", str(audit.__dict__))
        self.assertEqual(person_of("parent-02").contact_email, "family01@example.invalid")

    def test_nespremenjen_in_prazen_naslov(self):
        client = self.login()
        client.post(self.url(), {"contact_email": "family01@example.invalid"})
        self.assertFalse(m.ChangeAudit.objects.filter(action="person.contact_updated").exists())
        client.post(self.url(), {"contact_email": ""})
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.contact_email, "")


class ImportScreenTests(ScreenBase):
    def preview(self, client=None, **override):
        client = client or self.login()
        r = client.post(f"{BASE}/uvoz/", {"source": "zaslon-test", "files": csv_files(**override)})
        self.assertEqual(r.status_code, 302, r.content[:500])
        return m.ImportBatch.objects.get(pk=r["Location"].rstrip("/").split("/")[-1])

    def test_predogled_ne_spremeni_evidence_in_hrani_datoteke(self):
        before = m.Person.objects.count()
        batch = self.preview()
        self.assertEqual(batch.status, m.ImportBatch.Status.PREVIEWED)
        self.assertEqual(m.Person.objects.count(), before)
        self.assertEqual(batch.uploads.count(), len(list(DATA.glob("*.csv"))))
        r = self.client.get(f"{BASE}/uvoz/{batch.pk}/")
        self.assert_accessible(r)
        self.assertContains(r, "Uveljavi serijo")

    def test_uveljavitev_in_izbris_datotek(self):
        batch = self.preview()
        r = self.client.post(f"{BASE}/uvoz/{batch.pk}/uveljavi/")
        self.assertRedirects(r, f"{BASE}/uvoz/{batch.pk}/")
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.APPLIED)
        self.assertFalse(batch.uploads.exists())
        self.assertTrue(m.SourceMapping.objects.filter(source="zaslon-test").exists())
        self.assertNotContains(self.client.get(f"{BASE}/uvoz/{batch.pk}/"), "Uveljavi serijo")

    def test_zavrzen_predogled(self):
        batch = self.preview()
        self.client.post(f"{BASE}/uvoz/{batch.pk}/zavrzi/")
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.REJECTED)
        self.assertFalse(batch.uploads.exists())
        self.assertFalse(m.SourceMapping.objects.filter(source="zaslon-test").exists())

    def test_napacna_datoteka_zavrne_serijo_brez_hrambe(self):
        batch = self.preview(persons=b"napacna;glava\nx;y\n")
        self.assertEqual(batch.status, m.ImportBatch.Status.REJECTED)
        self.assertFalse(batch.uploads.exists())
        r = self.client.get(f"{BASE}/uvoz/{batch.pk}/")
        self.assertContains(r, "bad_header")
        self.assertNotContains(r, "Uveljavi serijo")
        p = self.assert_accessible(r)
        self.assertEqual(len([a for t, a in p.tags if a.get("role") == "alert"]), 1)

    def test_brez_datotek_in_podvojena_datoteka(self):
        client = self.login()
        r = client.post(f"{BASE}/uvoz/", {"source": "zaslon-test"})
        self.assertEqual(r.status_code, 200)
        self.assert_accessible(r)
        self.assertContains(r, "Izberite vsaj eno datoteko CSV.")
        dup = csv_files()[:1] * 2
        dup = [SimpleUploadedFile(f.name, b"class_key;name;school_year\n") for f in dup]
        r = client.post(f"{BASE}/uvoz/", {"source": "zaslon-test", "files": dup})
        self.assertContains(r, "izbrana dvakrat")
        r = client.post(f"{BASE}/uvoz/", {"source": "Neveljaven vir!", "files": csv_files()})
        self.assertContains(r, "male črke")

    def test_sprememba_evidence_po_predogledu(self):
        self.preview()
        self.client.post(
            f"{BASE}/uvoz/{m.ImportBatch.objects.first().pk}/uveljavi/"
        )  # prva uveljavitev
        batch = self.preview()
        mp = m.SourceMapping.objects.get(source="zaslon-test", source_key="staff-01")
        m.Person.objects.filter(pk=mp.target_id).update(display_name="Ročno")
        self.client.post(f"{BASE}/uvoz/{batch.pk}/uveljavi/")
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.REJECTED)
        self.assertIn("preview_stale", {p["code"] for p in batch.problems})
        self.assertEqual(m.Person.objects.get(pk=mp.target_id).display_name, "Ročno")

    def test_stare_zacasne_datoteke_se_izbrisejo(self):
        batch = self.preview()
        batch.uploads.update(created_at=timezone.now() - timedelta(hours=25))
        self.client.get(f"{BASE}/uvoz/")
        self.assertFalse(batch.uploads.exists())
        r = self.client.post(f"{BASE}/uvoz/{batch.pk}/uveljavi/", follow=True)
        self.assertContains(r, "niso več na voljo")

    def test_stars_ne_more_uveljaviti(self):
        batch = self.preview()
        client = self.login("parent-01", Client())
        self.assertEqual(client.post(f"{BASE}/uvoz/{batch.pk}/uveljavi/").status_code, 403)
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.PREVIEWED)

    def test_get_ne_uveljavi(self):
        batch = self.preview()
        self.assertEqual(self.client.get(f"{BASE}/uvoz/{batch.pk}/uveljavi/").status_code, 405)
