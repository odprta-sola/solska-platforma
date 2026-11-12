"""Izvoz podatkov ene osebe (zahteva po dostopu, čl. 15 in 20; D07)."""

import json

from django.apps import apps
from django.db import models as dj
from django.test import Client

from registry import authz, export
from registry import models as m

from .test_zasloni import BASE, ScreenBase, person_of

# Vsak model s tujim ključem na osebo mora biti v izvozu ali namenoma izpuščen z razlogom.
COVERED = {
    "PersonRole",
    "Account",
    "Student",
    "StaffAssignment",
    "Relationship",
    "Grant",
    "Approval",
    "ScopeRef",
    "AudienceMember",
    "AudienceSnapshot",
    "ChangeAudit",
    "AccessAudit",
    "ImportBatch",
}
EXCLUDED = {}  # model: razlog


class PersonExportTests(ScreenBase):
    def url(self, person):
        return f"{BASE}/osebe/{person.pk}/izvoz/"

    def download(self, person, client=None):
        r = (client or self.login()).post(self.url(person))
        self.assertEqual(r.status_code, 200)
        return r, json.loads(r.content)

    def test_prenos_za_starsa(self):
        r, data = self.download(self.p1)
        self.assertTrue(r["Content-Disposition"].startswith("attachment;"))
        self.assertIn(str(self.p1.pk), r["Content-Disposition"])
        self.assertEqual(r["Cache-Control"], "no-store")
        self.assertEqual(data["format"], export.FORMAT)
        self.assertEqual(data["oseba"]["id"], str(self.p1.pk))
        self.assertEqual(data["oseba"]["e_naslov"], self.p1.contact_email)
        self.assertEqual(data["racun"]["uporabnisko_ime"], "parent-01")
        self.assertEqual(
            {x["ucenec"] for x in data["povezave_kot_stars"]},
            {
                r.student.person.display_name
                for r in m.Relationship.objects.filter(guardian=self.p1)
            },
        )
        self.assertEqual(len(data["upravicenja"]), m.Grant.objects.filter(person=self.p1).count())
        self.assertTrue(all(g["ucenec"] for g in data["upravicenja"]))
        self.assertEqual(data["izvorni_kljuci"], [{"vir": "testni-nabor", "kljuc": "parent-01"}])

    def test_brez_gesla_in_brez_tujih_podatkov(self):
        r, _ = self.download(self.p1)
        text = r.content.decode()
        self.assertNotIn(m.Account.objects.get(username="parent-01").password, text)
        self.assertNotIn("password", text)
        others = m.Person.objects.exclude(contact_email__in=["", self.p1.contact_email])
        self.assertTrue(others.exists())
        for other in others:
            self.assertNotIn(other.contact_email, text)
        for rel in m.Relationship.objects.filter(guardian=self.p1):
            self.assertNotIn(str(rel.student.person.pk), text)  # samo ime otroka, ne ID

    def test_sprememba_brez_imena_zaposlenega_in_vpogledi(self):
        client = self.login()
        rel = m.Relationship.objects.filter(guardian=self.p1).first()
        client.post(f"{BASE}/osebe/{self.p1.pk}/povezave/{rel.pk}/odvzem/")
        client.get(f"{BASE}/osebe/{self.p1.pk}/")
        r, data = self.download(self.p1, client)
        self.assertIn("relationship.revoked", {a["dejanje"] for a in data["spremembe_podatkov"]})
        self.assertNotIn(self.office.display_name, r.content.decode())
        screens = [v["zaslon"] for v in data["vpogledi_v_podatke"]]
        self.assertIn("oseba", screens)
        self.assertEqual(screens[-1], "izvoz")  # zapis nastane pred izvozom

    def test_lastna_dejanja_zaposlenega_brez_sklicev(self):
        client = self.login()
        client.get(f"{BASE}/osebe/{self.p1.pk}/")
        authz.revoke_grant(m.Grant.objects.filter(person=self.p1).first(), actor=self.office)
        _, data = self.download(self.office, client)
        own = data["lastna_dejanja"]
        self.assertIn("grant.revoked", {a["dejanje"] for a in own["spremembe"]})
        self.assertIn("oseba", {a["zaslon"] for a in own["vpogledi"]})
        text = json.dumps(own)
        self.assertNotIn(str(self.p1.pk), text)  # tuje entitete niso navedene

    def test_obcinstvo_pri_avtorju_in_prejemniku(self):
        staff = self.login("staff-01", Client())
        class_id = staff.get("/p0/api/v1/me/classes").json()["classes"][0]["class_id"]
        r = staff.post(
            "/p0/api/v1/audiences/resolve",
            {"class_id": class_id, "purpose": "notice"},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)
        _, parent = self.download(self.p1)
        _, author = self.download(person_of("staff-01"))
        self.assertTrue(parent["obcinstva_kot_prejemnik"])
        self.assertEqual(parent["obcinstva_kot_prejemnik"][0]["namen"], "notice")
        self.assertEqual(len(author["lastna_dejanja"]["obcinstva"]), 1)
        self.assertEqual(
            author["dodelitve_oddelkom"][0]["oddelek"],
            parent["obcinstva_kot_prejemnik"][0]["oddelek"],
        )

    def test_ucenec_z_oddelkom_in_starsi(self):
        student = m.Relationship.objects.filter(guardian=self.p1).first().student.person
        _, data = self.download(student)
        self.assertTrue(data["oddelki_ucenca"])
        self.assertIn(self.p1.display_name, {x["stars"] for x in data["povezave_kot_ucenec"]})
        self.assertIsNone(data["racun"])

    def test_dostop_in_metoda(self):
        url = self.url(self.p1)
        self.assertEqual(self.login().get(url).status_code, 405)
        self.assertEqual(Client().post(url).status_code, 302)  # prijava
        self.assertEqual(self.login("parent-01", Client()).post(url).status_code, 403)
        csrf = self.login(client=Client(enforce_csrf_checks=True))
        self.assertEqual(csrf.post(url).status_code, 403)
        missing = f"{BASE}/osebe/00000000-0000-0000-0000-000000000000/izvoz/"
        self.assertEqual(self.login().post(missing).status_code, 404)
        self.assertFalse(m.AccessAudit.objects.filter(screen="izvoz").exists())

    def test_gumb_na_strani_osebe(self):
        r = self.login().get(f"{BASE}/osebe/{self.p1.pk}/")
        self.assertContains(r, f'action="{self.url(self.p1)}"')

    def test_vsi_modeli_z_osebo_so_zajeti(self):
        linked = {
            model.__name__
            for model in apps.get_app_config("registry").get_models()
            for f in model._meta.get_fields()
            if isinstance(f, (dj.ForeignKey, dj.OneToOneField)) and f.related_model is m.Person
        }
        self.assertEqual(linked, COVERED | set(EXCLUDED))
