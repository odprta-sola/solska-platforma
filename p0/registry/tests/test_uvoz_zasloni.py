"""Uporabnost uvoza in zaslonov po ponovnem pregledu (R-03, R-04, R-08; DeepSeek R-02, R-06)."""

import csv
import re
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from registry import authz, importer
from registry import models as m

from .test_import import SRC, ImportBase, counts
from .test_zasloni import BASE, ScreenBase, csv_files

HEADER = b"source_person_key;display_name;contact_email\n"


class CsvLimitTests(ImportBase):
    def problems(self, files):
        before = counts()
        _, result = importer.preview(files, SRC, self.actor)
        self.assertFalse(result.clean)
        self.assertEqual(counts(), before)  # brez delnih sprememb
        return {p.code for p in result.problems}

    def test_polje_daljse_od_meje_razclenjevalnika(self):
        files = {"persons": HEADER + b"x;" + b"x" * 131073 + b";\n"}
        self.assertIn("too_long", self.problems(files))

    def test_dolzine_po_modelih(self):
        cases = {
            "display_name": HEADER + b"p1;" + b"x" * 201 + b";\n",
            "kljuc": HEADER + b"k" * 65 + b";Ime;\n",
            "email": HEADER + b"p1;Ime;" + b"a" * 250 + b"@b.si\n",
        }
        for label, content in cases.items():
            with self.subTest(label=label):
                self.assertIn("too_long", self.problems({"persons": content}))

    def test_meje_so_dovoljene(self):
        content = HEADER + b"k" * 64 + b";" + b"x" * 200 + b";\n"
        _, result = importer.preview({"persons": content}, SRC, self.actor)
        self.assertTrue(result.clean, [p.as_dict() for p in result.problems])

    def test_napaka_razclenjevalnika_je_tezava_predogleda(self):
        """Prava napaka csv (polje nad začasno znižano mejo) postane bad_csv, ne 500."""
        old = csv.field_size_limit(10)
        try:
            self.assertIn(
                "bad_csv", self.problems({"persons": HEADER + b"p1;" + b"x" * 20 + b";\n"})
            )
            self.assertIn("bad_csv", self.problems({"persons": b"x" * 20 + b";b\n1;2\n"}))
        finally:
            csv.field_size_limit(old)

    def test_obstojece_napake_ostanejo(self):
        self.assertIn("bad_encoding", self.problems({"persons": HEADER + b"p1;\xff;\n"}))
        self.assertIn("bad_header", self.problems({"persons": b"a;b\n1;2\n"}))
        self.assertIn("bad_row", self.problems({"persons": HEADER + b"p1;Ime;a@b.si;odvec\n"}))


class ScreenErrorTests(ScreenBase):
    def test_predolgo_polje_v_zaslonu_ni_500(self):
        f = [SimpleUploadedFile("persons.csv", HEADER + b"x;" + b"x" * 131073 + b";\n")]
        r = self.login().post(f"{BASE}/uvoz/", {"source": "dolg", "files": f}, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "too_long")
        self.assertNotContains(r, "Uveljavi serijo")


class PreviewPagingTests(ScreenBase):
    def big_preview(self, client, n=501):
        rows = "".join(f"person-{i:04};Oseba {i:04};\n" for i in range(n))
        f = [SimpleUploadedFile("persons.csv", HEADER + rows.encode())]
        r = client.post(f"{BASE}/uvoz/", {"source": "velik", "files": f})
        return r["Location"]

    def test_vsaka_postavka_je_dosegljiva(self):
        client = self.login()
        url = self.big_preview(client)
        seen, page = set(), 1
        while True:
            html = client.get(url, {"stran": page}).content.decode()
            seen |= {f"person-{i:04}" for i in range(501) if f"person-{i:04}" in html}
            if "Naslednja stran" not in html:
                break
            page += 1
        self.assertEqual(len(seen), 501)
        self.assertIn("person-0500", client.get(url, {"stran": page}).content.decode())

    def test_sprememba_za_prvimi_500_nespremenjenimi(self):
        client = self.login()
        url = self.big_preview(client, 500)
        client.post(url + "uveljavi/")
        rows = "".join(f"person-{i:04};Oseba {i:04};\n" for i in range(500)) + "nova;Nova oseba;\n"
        f = [SimpleUploadedFile("persons.csv", HEADER + rows.encode())]
        r = client.post(f"{BASE}/uvoz/", {"source": "velik", "files": f})
        html = client.get(r["Location"], {"samo": "spremembe"}).content.decode()
        self.assertIn("nova", html)
        self.assertNotIn("person-0000", html)
        self.assertIn("Prikazane so samo spremembe (1)", html)

    def test_vrstni_red_je_stabilen(self):
        client = self.login()
        url = self.big_preview(client)
        keys = lambda: re.findall(r"person-\d{4}", client.get(url, {"stran": 2}).content.decode())  # noqa: E731
        first = keys()
        self.assertEqual(first, keys())
        self.assertEqual(first, sorted(first))
        self.assertEqual(len(first), 200)


class DiscardOutcomeTests(ScreenBase):
    def preview(self, client):
        r = client.post(f"{BASE}/uvoz/", {"source": "zavrzi", "files": csv_files()})
        return r["Location"]

    def test_zavrzenje_po_uveljavitvi_v_drugi_seji(self):
        a, b = self.login(), self.login(client=type(self.client)())
        url = self.preview(a)
        a.post(url + "uveljavi/")
        r = b.post(url + "zavrzi/", follow=True)
        batch = m.ImportBatch.objects.get(pk=url.rstrip("/").split("/")[-1])
        self.assertEqual(batch.status, m.ImportBatch.Status.APPLIED)
        self.assertNotContains(r, "nič ni bilo spremenjeno")
        self.assertContains(r, "Zavrženje ni bilo izvedeno")

    def test_ze_zavrzena_serija(self):
        client = self.login()
        url = self.preview(client)
        client.post(url + "zavrzi/")
        r = client.post(url + "zavrzi/", follow=True)
        self.assertContains(r, "Zavrženje ni bilo izvedeno")

    def test_zavrzenje_predogleda(self):
        client = self.login()
        url = self.preview(client)
        r = client.post(url + "zavrzi/", follow=True)
        self.assertContains(r, "nič ni bilo spremenjeno")


class FutureValidityTests(ScreenBase):
    def test_prihodnja_povezava_in_upravicenje(self):
        later = timezone.now() + timedelta(days=30)
        rel = m.Relationship.objects.get(guardian=self.p2)
        m.Relationship.objects.filter(pk=rel.pk).update(valid_from=later)
        m.Grant.objects.filter(person=self.p2).update(valid_from=later)
        client = self.login()
        html = client.get(f"{BASE}/osebe/{self.p2.pk}/").content.decode()
        self.assertIn("še ne velja", html)
        self.assertNotIn("zaključen", html)
        self.assertIn("Odvzemi povezavo", html)
        client.post(f"{BASE}/osebe/{self.p2.pk}/povezave/{rel.pk}/odvzem/")
        rel.refresh_from_db()
        self.assertIsNotNone(rel.valid_until)
        self.assertGreater(rel.valid_until, rel.valid_from)
        scope = m.Grant.objects.filter(person=self.p2).first().scope_key
        after = later + timedelta(seconds=1)
        self.assertFalse(authz.check_grant(self.p2, scope, "acknowledge", at=after)[0])
