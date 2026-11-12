"""Napake API, format časa in pogodbeni preverjevalnik po ponovnem pregledu (R-01, R-02, R-06)."""

import json
from datetime import timedelta
from unittest import mock

from django.db import OperationalError
from django.test import Client, override_settings
from django.utils import timezone
from jsonschema import Draft202012Validator

from registry.contract_schemas import parse_date_time

from .contract_check import ContractViolation, check_response, validate
from .test_contract import M1, P0, ContractBase, delivery_body, person_of

VALID_TIMES = [
    "2099-01-01T00:00:00Z",
    "2099-01-01T00:00:00+00:00",
    "2099-01-01T00:00:00.123456-02:30",
    "2099-01-01t00:00:00z",
]
INVALID_TIMES = [
    "2099-01-01X00:00:00+00:00",
    "2099-01-01 00:00:00+00:00",
    "2099-01-01T00:00:00",
    "2099-01-01",
    "20990101T000000Z",
    "2099-13-01T00:00:00Z",
    "2099-02-30T00:00:00Z",
    "2099-01-01T25:00:00Z",
    "2099-01-01T00:00:00+0000",
]


class DateTimeFormatTests(ContractBase):
    def test_skladno_s_pogodbenim_preverjevalnikom(self):
        checker = Draft202012Validator.FORMAT_CHECKER
        for value in VALID_TIMES + INVALID_TIMES:
            with self.subTest(value=value):
                self.assertEqual(
                    parse_date_time(value) is not None, checker.conforms(value, "date-time")
                )

    def test_dostavna_zahteva_zavrne_neveljaven_cas(self):
        p1 = str(person_of("parent-01").pk)
        ref = self.ref("parent-01", "Učenec Testni 01")
        for i, value in enumerate(INVALID_TIMES):
            with self.subTest(value=value):
                body = delivery_body([(p1, ref)], key=f"neveljaven-{i}", expires_at=value)
                r = self.call("post", f"{M1}/delivery-requests", token=self.t_m2, body=body)
                self.assertEqual(r.status_code, 400)
        for i, value in enumerate(VALID_TIMES):
            with self.subTest(value=value):
                body = delivery_body([(p1, ref)], key=f"veljaven-{i}", expires_at=value)
                r = self.call("post", f"{M1}/delivery-requests", token=self.t_m2, body=body)
                self.assertEqual(r.status_code, 202)

    def test_ponovitev_po_izteku_ostane(self):
        p1 = str(person_of("parent-01").pk)
        ref = self.ref("parent-01", "Učenec Testni 01")
        now = timezone.now()
        expires = (now + timedelta(seconds=5)).isoformat()
        body = delivery_body([(p1, ref)], key="iztek", expires_at=expires)
        a = self.call("post", f"{M1}/delivery-requests", token=self.t_m2, body=body)
        with mock.patch("stubs.m1.timezone.now", return_value=now + timedelta(seconds=10)):
            b = self.call("post", f"{M1}/delivery-requests", token=self.t_m2, body=body)
        self.assertEqual((a.status_code, b.status_code), (202, 202))


class ApiErrorEdgeTests(ContractBase):
    def big_body_check(self):
        client = self.session("parent-01")
        body = json.dumps({"scope_ref": "x" * 200, "permission": "m1.confirm"})
        with override_settings(DATA_UPLOAD_MAX_MEMORY_SIZE=100):
            return client.post(
                f"{P0}/authorizations/check", data=body, content_type="application/json"
            )

    def test_preveliko_telo_je_json(self):
        for debug in (False, True):
            with self.subTest(debug=debug), override_settings(DEBUG=debug):
                r = self.big_body_check()
                self.assertEqual(r.status_code, 400)
                self.assertEqual(r["Content-Type"], "application/json")
                validate("Error", r.json())

    def audience(self, class_id):
        staff = person_of("staff-01")
        client = Client(raise_request_exception=False)
        return self.call(
            "post",
            f"{P0}/audiences/resolve",
            token=self.t_m1,
            client=client,
            body={"author_id": str(staff.pk), "class_id": class_id, "purpose": "notice"},
        )

    def test_class_id_ni_500(self):
        for value in ("²", "١", " 1", "1 ", "-1", "1.0", "9" * 19, "9" * 400):
            with self.subTest(value=value):
                r = self.audience(value)
                self.assertIn(r.status_code, (400, 403))
                validate("Error", r.json())
        self.assertEqual(self.audience("").status_code, 400)

    def test_obstojece_napake_ostanejo(self):
        c = Client(enforce_csrf_checks=True)
        from registry import models as m

        c.force_login(m.Account.objects.get(username="parent-01"))
        r = c.post(f"{P0}/authorizations/check", data="{}", content_type="application/json")
        self.assertEqual((r.status_code, r.json()["code"]), (403, "csrf_failed"))
        r = self.session("parent-01").post(f"{P0}/me")
        self.assertEqual((r.status_code, r["Allow"]), (405, "GET"))
        client = self.session("parent-01")
        client.raise_request_exception = False
        ref = self.ref("parent-01", "Učenec Testni 01")
        with mock.patch("registry.authz.check_scope", side_effect=OperationalError("x")):
            r = client.post(
                f"{P0}/authorizations/check",
                data=json.dumps({"scope_ref": ref, "permission": "m1.confirm"}),
                content_type="application/json",
            )
        self.assertEqual(r.status_code, 503)
        with mock.patch("registry.api.timezone.now", side_effect=RuntimeError("skrito")):
            r = client.get(f"{P0}/me/relationships")
        self.assertEqual(r.status_code, 500)
        self.assertNotIn("skrito", r.content.decode())


class CheckerUnknownPathTests(ContractBase):
    def test_neznana_pot_api_pade(self):
        for path in ("/p0/api/v1/typo", "/m1/api/v1/neznano", "/m2/api/v1/x"):
            with self.subTest(path=path), self.assertRaises(ContractViolation):
                check_response("post", path, 200, "text/html", b"not JSON")

    def test_napacna_metoda_status_medij_telo(self):
        ok = json.dumps({"code": "x", "message": "", "trace_id": "t"}).encode()
        with self.assertRaises(ContractViolation):
            check_response("put", f"{P0}/me", 200, "application/json", ok)
        with self.assertRaises(ContractViolation):
            check_response("get", f"{P0}/me", 418, "application/json", ok)
        with self.assertRaises(ContractViolation):
            check_response("get", f"{P0}/me", 401, "text/html", ok)
        with self.assertRaises(ContractViolation):
            check_response("get", f"{P0}/me", 401, "application/json", b"{}")

    def test_namerne_pomozne_poti_so_izvzete(self):
        check_response("post", "/m1/api/v1/_stub/advance", 200, "application/json", b"{}")
        check_response("get", "/p0/api/v1/health", 200, "application/json", b"{}")
        check_response("get", "/accounts/login/", 200, "text/html", b"<html>")
