"""Odjemalec API za module (D12, C05): servisni in uporabniški klic, napake in nedosegljivost."""

from django.core.management import call_command
from django.test import Client, TestCase

from core.api_client import Api, ApiError, Unavailable, UserSession
from core.testing import DjangoClientTransport
from registry import models as m
from registry import services


class FakeTransport:
    def __init__(self, status, raw):
        self.status, self.raw = status, raw

    def send(self, method, url, headers, body):
        return self.status, self.raw


class ApiClientTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_test_data", verbosity=0)
        _, cls.token = services.create_service_client("m1", ["p0.authorizations.check"])

    def setUp(self):
        self.transport = DjangoClientTransport()
        self.api = Api(base_url="http://testserver", transport=self.transport)

    def session_of(self, username):
        browser = Client()
        browser.force_login(m.Account.objects.get(username=username))
        browser.get("/p0/api/v1/me")  # vzpostavi sejo
        browser.cookies["csrftoken"] = "a" * 32
        return UserSession(
            session_id=browser.cookies["sessionid"].value,
            csrf_token="a" * 32,
            origin="http://testserver",
        )

    def test_servisni_klic_z_zetonom(self):
        body = {"subject_id": "ni-uuid", "scope_ref": "sr_x", "permission": "m1.confirm"}
        r = self.api.call("POST", "/p0/api/v1/authorizations/check", body, token=self.token)
        self.assertEqual(r["allowed"], False)
        self.assertTrue(self.transport.requests[0][2]["Authorization"].startswith("Bearer "))

    def test_napacen_zeton_je_api_napaka(self):
        with self.assertRaises(ApiError) as ctx:
            self.api.call("POST", "/p0/api/v1/authorizations/check", {}, token="svc_napacen")
        self.assertEqual(ctx.exception.status, 401)

    def test_uporabniski_klic_s_sejo_in_csrf(self):
        session = self.session_of("staff-01")
        classes = self.api.call("GET", "/p0/api/v1/me/classes", session=session)["classes"]
        body = {"class_id": classes[0]["class_id"], "purpose": "notice"}
        r = self.api.call("POST", "/p0/api/v1/audiences/resolve", body, session=session)
        self.assertTrue(r["audience_ref"].startswith("au_"))

    def test_brez_csrf_zavrnjen(self):
        s = self.session_of("staff-01")
        no_csrf = UserSession(session_id=s.session_id, csrf_token="", origin=s.origin)
        with self.assertRaises(ApiError) as ctx:
            self.api.call("POST", "/p0/api/v1/audiences/resolve", {}, session=no_csrf)
        self.assertEqual(ctx.exception.status, 403)

    def test_5xx_in_ne_json_sta_nedosegljivost(self):
        for status, raw in ((503, b'{"code": "unavailable"}'), (500, b"{}"), (200, b"<html>")):
            with self.subTest(status=status), self.assertRaises(Unavailable):
                Api(base_url="http://x", transport=FakeTransport(status, raw)).call("GET", "/p")

    def test_omrezna_napaka_in_shema(self):
        with self.assertRaises(Unavailable):
            Api(base_url="http://127.0.0.1:9").call("GET", "/p0/api/v1/me")
        with self.assertRaises(Unavailable):
            Api(base_url="file:///etc").call("GET", "/passwd")
