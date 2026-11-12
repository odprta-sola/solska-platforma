"""Varovala uvoza, kontaktov in prijave (regresijski testi)."""

import json
from unittest import mock

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.utils.http import int_to_base36

from registry import authz, importer, services
from registry import models as m
from registry.adapters import ClosedAccountAdapter
from registry.tests.test_import import SRC, ImportBase, counts, load

P0 = "/p0/api/v1"
NEW_FROM = "2026-09-02T00:00:00Z"


def shift(files, name, person_key, new_from=NEW_FROM, until="", rel_type=None):
    """Premakne valid_from (in po želji valid_until / vrsto) vrstic ene osebe v datoteki."""
    out = []
    for line in files[name].decode().splitlines():
        if line.startswith(f"{person_key};"):
            parts = line.split(";")
            parts[3] = new_from
            parts[4] = until
            if rel_type and name == "relationships":
                parts[2] = rel_type
            line = ";".join(parts)
        out.append(line)
    files[name] = ("\n".join(out) + "\n").encode()
    return files


class ImportRestrictionTests(ImportBase):
    def setUp(self):
        super().setUp()
        self.apply()
        self.p2 = m.Person.objects.get(pk=self.key("person", "parent-02"))
        self.p1 = m.Person.objects.get(pk=self.key("person", "parent-01"))
        s1 = self.key("person", "student-01")
        s2 = self.key("person", "student-02")
        self.scope1, self.scope2 = f"student:{s1}", f"student:{s2}"

    def allowed(self, person, scope):
        return authz.check_grant(person, scope, "acknowledge")[0]

    def revoke_relationship_p2(self):
        rel = m.Relationship.objects.get(guardian=self.p2)
        authz.revoke_relationship(rel, actor=self.actor, source="rocno")

    def revoke_grant_p1_s1(self):
        grant = m.Grant.objects.get(person=self.p1, scope_key=self.scope1)
        authz.revoke_grant(grant, actor=self.actor, source="rocno")

    def attempt(self, files):
        """Predogled in poskus uveljavitve; vrne kode težav. Neuspeh ne pusti sprememb."""
        before = counts()
        batch, result = importer.preview(files, SRC, self.actor)
        codes = {p.code for p in result.problems}
        if not result.clean:
            with self.assertRaises(ValueError):
                importer.apply_batch(batch, files, self.actor)
            self.assertEqual(counts(), before)
        else:
            importer.apply_batch(batch, files, self.actor)
        return codes

    def test_nespremenjen_uvoz_po_odvzemu_povezave(self):
        self.revoke_relationship_p2()
        self.assertIn("manual_restriction", self.attempt(load()))
        self.assertFalse(self.allowed(self.p2, self.scope1))

    def shifted_after_relationship_revoke(self, *names):
        self.revoke_relationship_p2()
        files = load()
        for name in names:
            shift(files, name, "parent-02")
        self.assertIn("manual_restriction", self.attempt(files))
        self.assertFalse(self.allowed(self.p2, self.scope1))
        self.assertEqual(m.Relationship.objects.active().filter(guardian=self.p2).count(), 0)

    def test_premaknjen_zacetek_povezave(self):
        self.shifted_after_relationship_revoke("relationships")

    def test_premaknjen_zacetek_granta(self):
        self.shifted_after_relationship_revoke("grants")

    def test_premaknjen_zacetek_obeh(self):
        self.shifted_after_relationship_revoke("relationships", "grants")

    def test_sprememba_vrste_povezave_ne_obide_odvzema(self):
        self.revoke_relationship_p2()
        files = shift(load(), "relationships", "parent-02", rel_type="guardian")
        shift(files, "grants", "parent-02")
        self.assertIn("manual_restriction", self.attempt(files))
        self.assertFalse(self.allowed(self.p2, self.scope1))

    def test_odvzem_enega_dovoljenja_ne_vpliva_na_drugega(self):
        self.revoke_grant_p1_s1()
        files = load()
        lines = files["grants"].decode().splitlines()
        files["grants"] = (
            "\n".join(
                line.replace("2026-09-01T00:00:00Z", NEW_FROM)
                if line.startswith("parent-01;student:student-01;")
                else line
                for line in lines
            )
            + "\n"
        ).encode()
        self.assertIn("manual_restriction", self.attempt(files))
        self.assertFalse(self.allowed(self.p1, self.scope1))
        self.assertTrue(self.allowed(self.p1, self.scope2))  # drugi otrok ostane
        self.assertTrue(self.allowed(self.p2, self.scope1))  # drug starš ostane

    def test_zgodovinski_zapis_pred_odvzemom_je_dovoljen(self):
        self.revoke_relationship_p2()
        files = shift(load(), "relationships", "parent-02", until="2026-10-01T00:00:00Z")
        shift(files, "grants", "parent-02", until="2026-10-01T00:00:00Z")
        self.assertNotIn("manual_restriction", self.attempt(files))
        self.assertFalse(self.allowed(self.p2, self.scope1))

    def test_sled_odvzema_ostane(self):
        self.revoke_relationship_p2()
        self.attempt(shift(load(), "relationships", "parent-02"))
        self.assertTrue(
            m.ChangeAudit.objects.filter(action="relationship.revoked", source="rocno").exists()
        )

    def test_vse_stiri_poti_po_poskusu_uvoza(self):
        self.revoke_relationship_p2()
        files = shift(load(), "relationships", "parent-02")
        shift(files, "grants", "parent-02")
        self.attempt(files)
        account = m.Account.objects.create(username="p2", person=self.p2)
        client = Client()
        client.force_login(account)
        rels = client.get(f"{P0}/me/relationships").json()["relationships"]
        self.assertEqual(rels, [])
        ref = services.issue_scope_ref(self.p2, self.scope1)
        r = client.post(
            f"{P0}/authorizations/check",
            data=json.dumps({"scope_ref": ref.ref, "permission": "m1.confirm"}),
            content_type="application/json",
        )
        self.assertFalse(r.json()["allowed"])
        _, token = services.create_service_client(
            "m1", ["p0.audiences.resolve", "p0.contacts.resolve"]
        )
        auth = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        staff = m.Person.objects.get(pk=self.key("person", "staff-01"))
        klass = m.StaffAssignment.objects.get(person=staff).school_class_id
        r = client.post(
            f"{P0}/audiences/resolve",
            data=json.dumps(
                {"author_id": str(staff.pk), "class_id": str(klass), "purpose": "notice"}
            ),
            content_type="application/json",
            **auth,
        )
        self.assertNotIn(str(self.p2.pk), {x["person_id"] for x in r.json()["recipients"]})
        with mock.patch("registry.api.delivery_binding_verified", return_value=True):
            r = Client().post(
                f"{P0}/delivery-contacts/resolve",
                data=json.dumps(
                    {
                        "recipient_id": str(self.p2.pk),
                        "scope_ref": ref.ref,
                        "delivery_request_id": "dr_x",
                    }
                ),
                content_type="application/json",
                **auth,
            )
        self.assertEqual(r.status_code, 403)


class ImportRoleTests(ImportBase):
    def with_role(self, role, person_key="staff-01"):
        files = load()
        files["roles"] = files["roles"] + f"{person_key};{role}\n".encode()
        return files

    def test_tajnistvo_ne_dodeli_skrbnika(self):
        _, result = importer.preview(self.with_role("admin"), SRC, self.actor)
        self.assertIn("role_not_authorized", {p.code for p in result.problems})
        self.assertFalse(m.PersonRole.objects.filter(role="admin").exists())

    def test_skrbnik_sme_dodeliti_skrbnika(self):
        m.PersonRole.objects.create(person=self.actor, role=m.Role.ADMIN)
        _, result = importer.preview(self.with_role("admin"), SRC, self.actor)
        self.assertTrue(result.clean, [p.as_dict() for p in result.problems])

    def test_tajnistvo_ne_dodeli_tajnistva(self):
        _, result = importer.preview(self.with_role("office"), SRC, self.actor)
        self.assertIn("role_not_authorized", {p.code for p in result.problems})

    def test_skrbnik_sme_dodeliti_tajnistvo(self):
        m.PersonRole.objects.create(person=self.actor, role=m.Role.ADMIN)
        _, result = importer.preview(self.with_role("office"), SRC, self.actor)
        self.assertTrue(result.clean, [p.as_dict() for p in result.problems])

    def test_ponovni_uvoz_obstojece_vloge_je_dovoljen(self):
        m.PersonRole.objects.create(person=self.actor, role=m.Role.ADMIN)
        files = self.with_role("office")
        batch, _ = importer.preview(files, SRC, self.actor)
        importer.apply_batch(batch, files, self.actor)
        m.PersonRole.objects.filter(person=self.actor, role=m.Role.ADMIN).delete()
        _, result = importer.preview(files, SRC, self.actor)  # tajništvo, ista vsebina
        self.assertTrue(result.clean, [p.as_dict() for p in result.problems])

    def test_tajnistvo_sme_dodeliti_ucitelja(self):
        _, result = importer.preview(self.with_role("teacher", "parent-04"), SRC, self.actor)
        self.assertTrue(result.clean)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordRecoveryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_test_data", verbosity=0)
        for name in ("parent-01", "parent-02"):
            a = m.Account.objects.get(username=name)
            a.set_password("testno-geslo-123!")
            a.save()

    def test_skupni_naslov_ne_izda_povezav(self):
        r = self.client.post("/accounts/password/reset/", {"email": "family01@example.invalid"})
        self.assertEqual(r.status_code, 404)
        self.assertEqual(len(mail.outbox), 0)

    def test_neobstojec_in_skupni_naslov_enak_odgovor(self):
        a = self.client.post("/accounts/password/reset/", {"email": "family01@example.invalid"})
        b = self.client.post("/accounts/password/reset/", {"email": "nihce@example.invalid"})
        self.assertEqual((a.status_code, a.content), (b.status_code, b.content))

    def test_neposredne_poti_zaprte(self):
        account = m.Account.objects.get(username="parent-01")
        uid = int_to_base36(account.pk)
        key = default_token_generator.make_token(account)  # prej izdana povezava
        for path in (
            "/accounts/password/reset/",
            "/accounts/password/reset/done/",
            "/accounts/password/reset/confirm/",
            "/accounts/password/reset/complete/",
            "/accounts/password/reset/key/done/",
            f"/accounts/password/reset/key/{uid}-{key}/",
            f"/accounts/password/reset/key/{uid}-set-password/",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)
                r = self.client.post(path, {"password1": "x", "password2": "x"})
                self.assertEqual(r.status_code, 404)
        account.refresh_from_db()
        self.assertTrue(account.check_password("testno-geslo-123!"))

    def test_adapter_ne_poslje_obnove(self):
        account = m.Account.objects.get(username="parent-01")
        ClosedAccountAdapter().send_password_reset_mail(account, account.email, {})
        self.assertEqual(len(mail.outbox), 0)

    def test_prijava_z_uporabniskim_imenom_in_locena_racuna(self):
        ids = set()
        for name in ("parent-01", "parent-02"):
            c = Client()
            r = c.post("/accounts/login/", {"login": name, "password": "testno-geslo-123!"})
            self.assertEqual(r.status_code, 302)
            ids.add(c.get(f"{P0}/me").json()["person_id"])
        self.assertEqual(len(ids), 2)

    def test_prijavni_obrazec_ne_kaze_obnove(self):
        html = self.client.get("/accounts/login/").content.decode()
        self.assertNotIn("/accounts/password/reset/", html)
