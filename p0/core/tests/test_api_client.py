"""Odjemalec API za module (D12, C05): servisni in uporabniški klic, napake in nedosegljivost."""

import http.server
import threading

from django.core.management import call_command
from django.test import Client, LiveServerTestCase, RequestFactory, SimpleTestCase, TestCase

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
        no_csrf = UserSession(session_id=s.session_id, csrf_token="")
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


class _Server:
    """Lokalni strežnik HTTP v niti; `reply(handler)` odgovori, `seen` hrani prejete glave."""

    def __init__(self, reply):
        server = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def _any(self):
                server.seen.append(dict(self.headers))
                reply(self)

            do_GET = do_POST = _any

            def log_message(self, *args):
                pass

        self.seen = []
        self.httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_port}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def _json(handler, status=200, body=b"{}"):
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class UrllibTransportTests(SimpleTestCase):
    """Pravi prenos HTTP (ne nadomestni): preusmeritve in neveljavni vhodi."""

    def server(self, reply):
        s = _Server(reply)
        self.addCleanup(s.close)
        return s

    def test_preusmeritev_ne_prenese_poverilnic(self):
        target = self.server(_json)
        session = UserSession(session_id="sid-x", csrf_token="c" * 32)

        def redirect(handler):
            handler.send_response(302)
            handler.send_header("Location", target.url + "/drugam")
            handler.send_header("Content-Type", "application/json")
            handler.send_header("Content-Length", "2")
            handler.end_headers()
            handler.wfile.write(b"{}")  # tudi veljaven JSON ob 3xx ni uspeh

        origin = self.server(redirect)
        api = Api(base_url=origin.url)
        for kwargs in ({"token": "svc_x"}, {"session": session}):
            for method, body in (("GET", None), ("POST", {})):
                with self.subTest(method=method, kind=list(kwargs)), self.assertRaises(Unavailable):
                    api.call(method, "/p0/api/v1/me", body, **kwargs)
        self.assertEqual(len(origin.seen), 4)
        self.assertEqual(target.seen, [])  # nov cilj ni prejel ničesar, tudi ne poverilnic

    def test_preusmeritev_na_isti_izvor_je_tudi_zavrnjena(self):
        def redirect(handler):
            if handler.path == "/drugam":
                return _json(handler)
            handler.send_response(301)
            handler.send_header("Location", "/drugam")
            handler.send_header("Content-Type", "application/json")
            handler.send_header("Content-Length", "2")
            handler.end_headers()
            handler.wfile.write(b"{}")

        s = self.server(redirect)
        with self.assertRaises(Unavailable):
            Api(base_url=s.url).call("GET", "/p", token="svc_x")
        self.assertEqual(len(s.seen), 1)

    def test_neposreden_odgovor_deluje(self):
        s = self.server(lambda h: _json(h, body=b'{"ok": true}'))
        self.assertEqual(Api(base_url=s.url).call("GET", "/p", token="svc_x"), {"ok": True})
        self.assertEqual(s.seen[0]["Authorization"], "Bearer svc_x")

    def test_napaka_4xx_ostane_api_napaka(self):
        s = self.server(lambda h: _json(h, 403, b'{"code": "scope_not_allowed"}'))
        with self.assertRaises(ApiError) as ctx:
            Api(base_url=s.url).call("GET", "/p", token="svc_x")
        self.assertEqual(ctx.exception.code, "scope_not_allowed")

    def test_neveljavna_glava_je_nedosegljivost(self):
        s = self.server(_json)
        bad = UserSession(session_id="s\r\nX-Probe: yes", csrf_token="")
        with self.assertRaises(Unavailable) as ctx:
            Api(base_url=s.url).call("GET", "/p", session=bad)
        self.assertNotIn("X-Probe", str(ctx.exception))
        self.assertEqual(s.seen, [])

    def test_skrajsan_odgovor_je_nedosegljivost(self):
        def truncated(handler):
            handler.send_response(200)
            handler.send_header("Content-Length", "100")
            handler.end_headers()
            handler.wfile.write(b'{"ok"')

        s = self.server(truncated)
        with self.assertRaises(Unavailable):
            Api(base_url=s.url).call("GET", "/p", token="svc_x")


class LiveUserSessionTests(LiveServerTestCase):
    """Uporabniški klic po pravem HTTP: brskalnikov izvor se razlikuje od notranjega naslova P0.

    Dokumentiran zagon: prijava na http://localhost:8000, modul kliče P0_API_URL
    (privzeto http://127.0.0.1:8000). Prej je prvi uporabniški POST vrnil 403 csrf_failed.
    """

    def setUp(self):
        call_command("seed_test_data", verbosity=0)

    def browser_request(self, username, host, secure=False):
        browser = Client()
        browser.force_login(m.Account.objects.get(username=username))
        request = RequestFactory().get("/m1/", HTTP_HOST=host, secure=secure)
        request.COOKIES = {"sessionid": browser.cookies["sessionid"].value, "csrftoken": "b" * 32}
        return request

    def test_post_z_drugacnim_izvorom_brskalnika(self):
        api = Api(base_url=self.live_server_url.replace("localhost", "127.0.0.1"))
        for host, secure in (("localhost:8000", False), ("sola.example.invalid", True)):
            with self.subTest(host=host):
                session = UserSession.from_request(self.browser_request("staff-01", host, secure))
                classes = api.call("GET", "/p0/api/v1/me/classes", session=session)["classes"]
                body = {"class_id": classes[0]["class_id"], "purpose": "notice"}
                r = api.call("POST", "/p0/api/v1/audiences/resolve", body, session=session)
                self.assertTrue(r["audience_ref"].startswith("au_"))

    def test_csrf_ostane_zahtevan(self):
        api = Api(base_url=self.live_server_url)
        s = UserSession.from_request(self.browser_request("staff-01", "localhost:8000"))
        for session in (
            UserSession(session_id=s.session_id, csrf_token=""),
            UserSession(session_id="neveljavna", csrf_token=s.csrf_token),
        ):
            with self.subTest(session=session.session_id[:4]), self.assertRaises(ApiError) as ctx:
                api.call("POST", "/p0/api/v1/audiences/resolve", {}, session=session)
            self.assertIn(ctx.exception.status, (401, 403))
