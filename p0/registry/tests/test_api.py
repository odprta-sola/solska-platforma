import json
from datetime import timedelta

from django.core.management import call_command
from django.test import Client, TestCase
from django.utils import timezone

from registry import authz
from registry import models as m


def person_of(key):
    mp = m.SourceMapping.objects.get(source_key=key, entity_type="person")
    return m.Person.objects.get(pk=mp.target_id)


class ApiBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_test_data", verbosity=0)

    def login(self, username, client=None):
        client = client or self.client
        client.force_login(m.Account.objects.get(username=username))
        return client

    def post_check(self, scope_key, permission="acknowledge", client=None):
        return (client or self.client).post(
            "/p0/api/v1/authorizations/check",
            data=json.dumps({"scope_key": scope_key, "permission": permission}),
            content_type="application/json",
        )

    def scope(self, student_key):
        return f"student:{person_of(student_key).pk}"


class AuthTests(ApiBase):
    def test_brez_prijave_401(self):
        for path in ("me", "me/relationships", "me/classes"):
            self.assertEqual(self.client.get(f"/p0/api/v1/{path}").status_code, 401)

    def test_prava_prijava_s_uporabniskim_imenom(self):
        account = m.Account.objects.get(username="parent-01")
        account.set_password("testno-geslo-123!")
        account.save()
        response = self.client.post(
            "/accounts/login/", {"login": "parent-01", "password": "testno-geslo-123!"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get("/p0/api/v1/me").status_code, 200)

    def test_racun_s_skupnim_naslovom_se_prijavi_locen(self):
        for name in ("parent-01", "parent-02"):
            a = m.Account.objects.get(username=name)
            a.set_password("testno-geslo-123!")
            a.save()
        c1, c2 = Client(), Client()
        c1.post("/accounts/login/", {"login": "parent-01", "password": "testno-geslo-123!"})
        c2.post("/accounts/login/", {"login": "parent-02", "password": "testno-geslo-123!"})
        n1 = c1.get("/p0/api/v1/me").json()["display_name"]
        n2 = c2.get("/p0/api/v1/me").json()["display_name"]
        self.assertNotEqual(n1, n2)

    def test_samoregistracije_ni(self):
        response = self.client.post(
            "/accounts/signup/",
            {"username": "nov", "password1": "testno-geslo-123!", "password2": "testno-geslo-123!"},
        )
        self.assertFalse(m.Account.objects.filter(username="nov").exists())
        self.assertIn(response.status_code, (200, 302, 403))

    def test_racun_brez_osebe_403(self):
        m.Account.objects.create(username="brez-osebe")
        self.login("brez-osebe")
        self.assertEqual(self.client.get("/p0/api/v1/me").status_code, 403)

    def test_post_zahteva_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.login("parent-01", client)
        response = self.post_check(self.scope("student-01"), client=client)
        self.assertEqual(response.status_code, 403)

    def test_odjava_konca_sejo(self):
        self.login("parent-01")
        self.client.post("/accounts/logout/")
        self.assertEqual(self.client.get("/p0/api/v1/me").status_code, 401)


class OwnDataTests(ApiBase):
    def test_me_vrne_samo_lastne_podatke(self):
        self.login("parent-01")
        data = self.client.get("/p0/api/v1/me").json()
        self.assertEqual(data["person_id"], str(person_of("parent-01").pk))
        self.assertEqual(data["roles"], ["parent"])

    def test_starsa_vidita_samo_svoje_otroke(self):
        self.login("parent-01")
        names = {
            r["student_display_name"]
            for r in self.client.get("/p0/api/v1/me/relationships").json()["relationships"]
        }
        self.assertEqual(names, {"Učenec Testni 01", "Učenec Testni 02"})
        self.login("parent-03")
        names = {
            r["student_display_name"]
            for r in self.client.get("/p0/api/v1/me/relationships").json()["relationships"]
        }
        self.assertEqual(names, {"Učenec Testni 03"})

    def test_ucitelj_vidi_samo_dodeljeni_oddelek(self):
        self.login("staff-01")
        keys = [c["class_key"] for c in self.client.get("/p0/api/v1/me/classes").json()["classes"]]
        self.assertEqual(keys, ["razred-7a"])

    def test_odvzeta_povezava_ni_vec_na_seznamu(self):
        rel = m.Relationship.objects.get(guardian=person_of("parent-02"))
        authz.revoke_relationship(rel)
        self.login("parent-02")
        self.assertEqual(self.client.get("/p0/api/v1/me/relationships").json()["relationships"], [])


class AuthorizationCheckTests(ApiBase):
    def test_lasten_otrok_dovoljen(self):
        self.login("parent-01")
        data = self.post_check(self.scope("student-01")).json()
        self.assertEqual(data, {"allowed": True, "reason": "ok"})

    def test_tuja_druzina_zavrnjena_brez_razkritja(self):
        self.login("parent-03")
        tuj = self.post_check(self.scope("student-01")).json()
        ugiban = self.post_check("student:00000000-0000-0000-0000-000000000000").json()
        self.assertEqual(tuj, {"allowed": False, "reason": "no_grant"})
        self.assertEqual(tuj, ugiban)

    def test_povezava_brez_upravicenja_ne_dovoli(self):
        m.Grant.objects.filter(person=person_of("parent-01")).delete()
        self.login("parent-01")
        self.assertFalse(self.post_check(self.scope("student-01")).json()["allowed"])

    def test_odvzem_povezave_prevlada_nad_upravicenjem(self):
        rel = m.Relationship.objects.get(guardian=person_of("parent-02"))
        authz.revoke_relationship(rel)
        self.login("parent-02")
        data = self.post_check(self.scope("student-01")).json()
        self.assertEqual(data, {"allowed": False, "reason": "relationship_inactive"})

    def test_odvzem_upravicenja_prevlada_nad_povezavo(self):
        authz.revoke_grant(m.Grant.objects.get(person=person_of("parent-02")))
        self.login("parent-02")
        self.assertFalse(self.post_check(self.scope("student-01")).json()["allowed"])

    def test_odvzem_pusti_sled(self):
        rel = m.Relationship.objects.get(guardian=person_of("parent-02"))
        authz.revoke_relationship(rel, actor=person_of("staff-03"), source="test")
        audit = m.ChangeAudit.objects.get(action="relationship.revoked")
        self.assertEqual(audit.entity_id, str(rel.pk))
        self.assertEqual(m.Relationship.objects.count(), 5)  # zapis ostane

    def test_potecno_upravicenje_ne_velja(self):
        grant = m.Grant.objects.get(person=person_of("parent-03"))
        grant.valid_until = timezone.now() - timedelta(seconds=1)
        grant.save()
        self.login("parent-03")
        self.assertFalse(self.post_check(self.scope("student-03")).json()["allowed"])

    def test_neveljavna_zahteva_400(self):
        self.login("parent-01")
        response = self.client.post(
            "/p0/api/v1/authorizations/check", data="ni json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.post_check(123).status_code, 400)
