"""Začetni zaslon m1: prijava prek seje P0, identiteta prek API, zavrnitev ob izpadu P0."""

from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from core.api_client import Api, Unavailable
from core.testing import DjangoClientTransport
from m1 import views
from m1.p0_client import Client


class HomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_test_data", verbosity=0)

    def setUp(self):
        self.transport = DjangoClientTransport()
        api = Api(base_url="http://testserver", transport=self.transport)
        patcher = mock.patch.object(views, "client", lambda: Client(api=api, token=""))
        patcher.start()
        self.addCleanup(patcher.stop)

    def login(self, username="parent-01"):
        from django.contrib.auth import get_user_model

        self.client.force_login(get_user_model().objects.get(username=username))

    def test_neprijavljen_na_prijavo(self):
        r = self.client.get("/m1/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r["Location"])

    def test_identiteta_iz_p0_prek_api(self):
        self.login()
        r = self.client.get("/m1/")
        self.assertContains(r, "Starš Testni 01")
        method, path, headers = self.transport.requests[0]
        self.assertEqual((method, path), ("GET", "/p0/api/v1/me"))
        self.assertIn("sessionid=", headers["Cookie"])
        self.assertNotIn("Authorization", headers)  # uporabniški klic, ne servisni

    def test_izpad_p0_zavrne(self):
        self.login()
        with mock.patch.object(Client, "me", side_effect=Unavailable("izpad")):
            r = self.client.get("/m1/")
        self.assertEqual(r.status_code, 503)
        self.assertNotContains(r, "Starš Testni 01", status_code=503)

    def test_osnovna_dostopnost(self):
        self.login()
        html = self.client.get("/m1/").content.decode()
        self.assertIn('<html lang="sl">', html)
        self.assertEqual(html.count("<h1"), 1)
        self.assertEqual(html.count("<main"), 1)
