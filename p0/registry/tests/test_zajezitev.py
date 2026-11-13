"""Ukazi za zajezitev ob kršitvi (SECURITY.md): servisni račun in seje."""

import io

from django.contrib.sessions.models import Session
from django.core.management import CommandError, call_command
from django.test import Client, TestCase

from registry import models as m
from registry import services

CHECK = "/p0/api/v1/authorizations/check"
BODY = {"subject_id": "ni-uuid", "scope_ref": "sr_x", "permission": "m1.confirm"}


def run(*args):
    out = io.StringIO()
    call_command(*args, stdout=out, stderr=out)
    return out.getvalue().strip()


class ServiceClientContainmentTests(TestCase):
    def setUp(self):
        _, self.token = services.create_service_client("m1", ["p0.authorizations.check"])

    def check(self, token):
        return (
            Client()
            .post(
                CHECK, BODY, content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {token}"
            )
            .status_code
        )

    def test_onemogocenje(self):
        self.assertEqual(self.check(self.token), 200)
        run("deactivate_service_client", "m1")
        self.assertEqual(self.check(self.token), 401)

    def test_zamenjava_zetona(self):
        run("deactivate_service_client", "m1")
        new = run("rotate_service_client", "m1")
        self.assertTrue(new.startswith("svc_"))
        self.assertEqual(self.check(self.token), 401)  # stari žeton ne velja več
        self.assertEqual(self.check(new), 200)  # novi velja, dovoljenja ostanejo
        self.assertEqual(m.ServiceClient.objects.get(name="m1").scopes, ["p0.authorizations.check"])

    def test_neobstojeci_racun(self):
        for command in ("deactivate_service_client", "rotate_service_client"):
            with self.subTest(command=command), self.assertRaises(CommandError):
                run(command, "m9")


class SessionPurgeTests(TestCase):
    def setUp(self):
        call_command("seed_test_data", verbosity=0)

    def test_izbris_vseh_sej_odjavi_in_ohrani_sledi(self):
        browser = Client()
        browser.force_login(m.Account.objects.get(username="parent-01"))
        self.assertEqual(browser.get("/p0/api/v1/me").status_code, 200)
        m.ChangeAudit.objects.create(action="x", entity_type="person", entity_id="1")
        m.AccessAudit.objects.create(screen="oseba", entity_type="person", entity_id="1")
        self.assertIn("Za izbris", run("purge_all_sessions"))  # brez --yes nič
        self.assertTrue(Session.objects.exists())
        run("purge_all_sessions", "--yes")
        self.assertFalse(Session.objects.exists())
        self.assertEqual(browser.get("/p0/api/v1/me").status_code, 401)
        self.assertEqual(m.ChangeAudit.objects.count(), 1)
        self.assertEqual(m.AccessAudit.objects.count(), 1)
