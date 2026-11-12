"""Robni primeri pogodbe, napak API, nadomestkov in uvoza (prvi neodvisni pregled P0)."""

import copy
import json
import threading
from datetime import timedelta
from unittest import mock

from django.db import OperationalError, connection
from django.test import Client, TransactionTestCase
from django.utils import timezone

from registry import importer
from registry import models as m
from registry.contract_schemas import REQUESTS

from .contract_check import SPEC, ContractViolation, check_response, validate
from .test_contract import M1, M2, P0, ContractBase, delivery_body, person_of
from .test_import import SRC, ImportBase, load


def resolved(schema):
    """Shema iz pogodbe z razrešenimi $ref in brez opisov."""
    if isinstance(schema, dict):
        if "$ref" in schema:
            name = schema["$ref"].rsplit("/", 1)[1]
            return resolved(SPEC["components"]["schemas"][name])
        return {k: resolved(v) for k, v in schema.items() if k != "description"}
    if isinstance(schema, list):
        return [resolved(v) for v in schema]
    return schema


def invalid_values(value):
    """Vrednosti napačnega tipa (in prazne) glede na veljavno vrednost polja."""
    if isinstance(value, str):
        return (123, None, ["x"], "")
    if isinstance(value, list):
        return (123, None, "x", [], [123])
    if isinstance(value, dict):
        return (123, None, "x", [])
    return (None, "x")


class RequestSchemaParity(ContractBase):
    def test_sheme_zahtev_v_p0_so_enake_pogodbi(self):
        for name, schema in REQUESTS.items():
            with self.subTest(schema=name):
                self.assertEqual(schema, resolved(SPEC["components"]["schemas"][name]))


class RequestValidation(ContractBase):
    """Iz shem pogodbe izpeljani neveljavni vhodi morajo vrniti 400 (ne 200/202)."""

    def setUp(self):
        super().setUp()
        self.p1 = str(person_of("parent-01").pk)
        self.ref1 = self.ref("parent-01", "Učenec Testni 01")
        staff = person_of("staff-01")
        self.class_id = str(m.StaffAssignment.objects.get(person=staff).school_class_id)
        self.author = str(staff.pk)

    def cases(self):
        created = self.call(
            "post",
            f"{M1}/delivery-requests",
            token=self.t_m2,
            body=delivery_body([(self.p1, self.ref1)], key="osnova"),
        ).json()
        rid, item = created["delivery_request_id"], created["recipients"][0]["item_id"]
        aud = self.audience()
        member = aud["recipients"][0]
        return [
            (
                "AuthCheckRequest",
                f"{P0}/authorizations/check",
                {"client": self.session("parent-01")},
                {"scope_ref": self.ref1, "permission": "m1.confirm", "subject_id": self.p1},
            ),
            (
                "AudienceRequest",
                f"{P0}/audiences/resolve",
                {"client": self.session("staff-01")},
                {"class_id": self.class_id, "purpose": "notice"},
            ),
            (
                "ContactRequest",
                f"{P0}/delivery-contacts/resolve",
                {"token": self.t_m1},
                {
                    "recipient_id": member["person_id"],
                    "scope_ref": member["scope_ref"],
                    "audience_ref": aud["audience_ref"],
                },
            ),
            (
                "DeliveryRequest",
                f"{M1}/delivery-requests",
                {"token": self.t_m2},
                delivery_body([(self.p1, self.ref1)], key="nov"),
            ),
            (
                "CancelRequest",
                f"{M1}/delivery-requests/{rid}/cancel",
                {"token": self.t_m2},
                {"item_ids": [item]},
            ),
            (
                "ReminderCheckRequest",
                f"{M2}/reminders/check",
                {"token": self.t_m1},
                {"need_ref": "n1", "recipient_id": self.p1, "scope_ref": self.ref1},
            ),
        ]

    def post(self, path, auth, body):
        return self.call("post", path, body=body, **auth)

    def test_veljaven_vhod_ni_zavrnjen_kot_neveljaven(self):
        for name, path, auth, body in self.cases():
            with self.subTest(schema=name):
                self.assertNotEqual(self.post(path, auth, body).status_code, 400)

    def test_manjkajoce_obvezno_polje(self):
        for name, path, auth, body in self.cases():
            for field in REQUESTS[name]["required"]:
                with self.subTest(schema=name, field=field):
                    bad = {k: v for k, v in body.items() if k != field}
                    self.assertEqual(self.post(path, auth, bad).status_code, 400)

    def test_dodatno_polje(self):
        for name, path, auth, body in self.cases():
            with self.subTest(schema=name):
                self.assertEqual(self.post(path, auth, {**body, "extra": 1}).status_code, 400)

    def test_napacen_tip_in_prazen_identifikator(self):
        for name, path, auth, body in self.cases():
            for field, value in body.items():
                for bad_value in invalid_values(value):
                    with self.subTest(schema=name, field=field, value=bad_value):
                        bad = {**body, field: bad_value}
                        self.assertEqual(self.post(path, auth, bad).status_code, 400)

    def test_ugnezdena_dodatna_polja_in_predolg_niz(self):
        _, path, auth, body = self.cases()[3]
        for mutate in (
            lambda b: b["recipients"][0].update(extra=1),
            lambda b: b["target"].update(extra=1),
            lambda b: b.update(template_id="x" * 257),
            lambda b: b.update(recipients=[b["recipients"][0]] * 201),
        ):
            bad = copy.deepcopy(body)
            mutate(bad)
            self.assertEqual(self.post(path, auth, bad).status_code, 400)

    def test_napacen_json(self):
        for _, path, auth, _ in self.cases():
            with self.subTest(path=path):
                client = auth.get("client") or Client()
                headers = (
                    {"HTTP_AUTHORIZATION": f"Bearer {auth['token']}"} if "token" in auth else {}
                )
                r = client.post(path, data="{ne-json", content_type="application/json", **headers)
                self.assertEqual(r.status_code, 400)
                validate("Error", r.json())


class ApiErrorContract(ContractBase):
    def test_neveljaven_uuid_ni_500(self):
        c = Client(raise_request_exception=False)
        r = self.call(
            "post",
            f"{P0}/authorizations/check",
            token=self.t_m1,
            client=c,
            body={"scope_ref": "sr_x", "permission": "m1.confirm", "subject_id": "not-a-uuid"},
        )
        self.assertEqual(r.json()["reason_code"], "NOT_ALLOWED")
        body = {"recipient_id": "not-a-uuid", "scope_ref": "sr_x", "audience_ref": "au_x"}
        r = self.call(
            "post", f"{P0}/delivery-contacts/resolve", token=self.t_m1, client=c, body=body
        )
        self.assertEqual(r.status_code, 403)

    def test_nedosegljiva_evidenca_je_503_ne_zavrnitev(self):
        ref = self.ref("parent-01", "Učenec Testni 01")
        client = self.session("parent-01")
        client.raise_request_exception = False
        for target in ("registry.authz.check_scope",):
            with mock.patch(target, side_effect=OperationalError("izpad")):
                r = self.call(
                    "post",
                    f"{P0}/authorizations/check",
                    client=client,
                    body={"scope_ref": ref, "permission": "m1.confirm"},
                )
            self.assertEqual(r.status_code, 503)
            self.assertNotIn("allowed", r.json())

    def test_nepricakovana_napaka_je_json_brez_podrobnosti(self):
        client = self.session("parent-01")
        client.raise_request_exception = False
        with mock.patch("registry.api.timezone.now", side_effect=RuntimeError("skrito-123")):
            r = client.get(f"{P0}/me/relationships")
        self.assertEqual(r.status_code, 500)
        validate("Error", r.json())
        self.assertNotIn("skrito-123", r.content.decode())

    def test_seja_brez_csrf_je_json_403(self):
        c = Client(enforce_csrf_checks=True)
        c.force_login(m.Account.objects.get(username="parent-01"))
        r = c.post(f"{P0}/authorizations/check", data="{}", content_type="application/json")
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r["Content-Type"], "application/json")
        self.assertEqual(r.json()["code"], "csrf_failed")

    def test_servisni_klic_brez_piskotkov_in_csrf(self):
        c = Client(enforce_csrf_checks=True)
        r = self.call(
            "post",
            f"{P0}/authorizations/check",
            token=self.t_m1,
            client=c,
            body={"scope_ref": "sr_x", "permission": "m1.confirm", "subject_id": "x"},
        )
        self.assertEqual(r.status_code, 200)

    def test_napacen_zeton_ob_veljavni_seji(self):
        client = self.session("parent-01")
        ref = self.ref("parent-01", "Učenec Testni 01")
        body = {"scope_ref": ref, "permission": "m1.confirm"}
        bad = self.call(
            "post", f"{P0}/authorizations/check", token="svc_x", client=client, body=body
        )
        self.assertEqual(bad.status_code, 401)
        good = self.call(
            "post",
            f"{P0}/authorizations/check",
            token=self.t_m1,
            client=client,
            body={**body, "subject_id": str(person_of("parent-01").pk)},
        )
        self.assertEqual(good.status_code, 200)  # servisna pot, seja ni upoštevana

    def test_napacna_metoda_in_neznana_pot(self):
        r = self.call("post", f"{P0}/me", client=self.session("parent-01"))
        self.assertEqual(r.status_code, 405)
        self.assertEqual(r["Allow"], "GET")
        validate("Error", r.json())
        r = self.session("parent-01").get(f"{P0}/ne-obstaja")
        self.assertEqual(r.status_code, 404)
        validate("Error", r.json())


class StubEdgeContract(ContractBase):
    def setUp(self):
        super().setUp()
        self.p1 = str(person_of("parent-01").pk)
        self.r1 = self.ref("parent-01", "Učenec Testni 01")
        self.r2 = self.ref("parent-01", "Učenec Testni 02")

    def create(self, refs, **kw):
        return self.call(
            "post", f"{M1}/delivery-requests", token=self.t_m2, body=delivery_body(refs, **kw)
        )

    def test_ista_oseba_dva_obsega_sta_dve_postavki(self):
        r = self.create([(self.p1, self.r1), (self.p1, self.r2)])
        self.assertEqual(r.status_code, 202)
        items = r.json()["recipients"]
        self.assertEqual({x["scope_ref"] for x in items}, {self.r1, self.r2})
        self.assertEqual(len({x["item_id"] for x in items}), 2)
        rid = r.json()["delivery_request_id"]
        self.call(
            "post",
            f"{M1}/delivery-requests/{rid}/cancel",
            token=self.t_m2,
            body={"item_ids": [items[0]["item_id"]]},
        )
        g = self.call("get", f"{M1}/delivery-requests/{rid}", token=self.t_m2).json()
        self.assertEqual(g["counts"], {"cancelled": 1, "queued": 1})  # drugi obseg ostane

    def test_isti_prejemnik_in_obseg_dvakrat(self):
        r = self.create([(self.p1, self.r1), (self.p1, self.r1)])
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["code"], "duplicate_recipient")

    def test_counts_ustreza_postavkam_in_selektiven_preklic(self):
        p2 = str(person_of("parent-02").pk)
        r = self.create([(self.p1, self.r1), (p2, self.ref("parent-02", "Učenec Testni 01"))])
        rid = r.json()["delivery_request_id"]
        first = next(x["item_id"] for x in r.json()["recipients"] if x["person_id"] == self.p1)
        self.call(
            "post",
            f"{M1}/delivery-requests/{rid}/cancel",
            token=self.t_m2,
            body={"item_ids": [first]},
        )
        g = self.call("get", f"{M1}/delivery-requests/{rid}", token=self.t_m2).json()
        self.assertEqual(g["counts"], {"cancelled": 1, "queued": 1})

    def test_ponovitev_po_izteku_vrne_isti_prevzem_brez_podaljsanja(self):
        now = timezone.now()
        expires = (now + timedelta(seconds=5)).isoformat()
        a = self.create([(self.p1, self.r1)], key="iztek", expires_at=expires)
        with mock.patch("stubs.m1.timezone.now", return_value=now + timedelta(seconds=10)):
            b = self.create([(self.p1, self.r1)], key="iztek", expires_at=expires)
            c = self.create([(self.p1, self.r1)], key="nov-po-izteku", expires_at=expires)
        self.assertEqual((a.status_code, b.status_code), (202, 202))
        self.assertEqual(a.json()["delivery_request_id"], b.json()["delivery_request_id"])
        self.assertEqual(c.status_code, 400)  # nova zahteva s pretečenim rokom

    def test_drugacna_vsebina_istega_kljuca_je_konflikt(self):
        self.create([(self.p1, self.r1)], key="k")
        r = self.create([(self.p1, self.r1)], key="k", template_id="drug")
        self.assertEqual(r.status_code, 409)


class CheckerSelfTest(ContractBase):
    """Preverjevalnik mora pasti pri namerno pokvarjenih odgovorih."""

    def bad(self, status, body, path=f"{P0}/authorizations/check", ct="application/json"):
        with self.assertRaises(ContractViolation):
            check_response("post", path, status, ct, json.dumps(body).encode())

    def ok(self, **over):
        return {
            "allowed": True,
            "reason_code": "ALLOWED",
            "checked_at": "2026-11-12T10:00:00Z",
            **over,
        }

    def test_veljaven_odgovor_uspe(self):
        check_response(
            "post",
            f"{P0}/authorizations/check",
            200,
            "application/json",
            json.dumps(self.ok()).encode(),
        )

    def test_pokvarjeni_odgovori(self):
        self.bad(200, self.ok(checked_at="not-a-date"))
        self.bad(200, {"allowed": True, "reason_code": "ALLOWED"})
        self.bad(200, self.ok(reason_code="NOT_ALLOWED"))  # logično neskladno
        self.bad(200, self.ok(allowed=False))
        self.bad(201, self.ok())  # status ni v pogodbi
        self.bad(500, {"code": "x", "message": "", "trace_id": "t"})
        self.bad(200, self.ok(), ct="text/html")
        path = f"{P0}/delivery-contacts/resolve"
        self.bad(
            200,
            {"deliverable": True, "reason_code": "OK", "email": "ni-naslov", "locale": "sl"},
            path,
        )
        self.bad(200, {"deliverable": True, "reason_code": "OK"}, path)
        self.bad(200, {"deliverable": False, "reason_code": "NO_CONTACT", "email": "a@b.si"}, path)
        self.bad(
            202,
            {
                "delivery_request_id": "d",
                "state": "queued",
                "recipients": [{"person_id": "p", "state": "queued"}],
                "counts": {"queued": 2},
            },
            f"{M1}/delivery-requests",
        )

    def test_dodatno_prepovedano_polje_v_zahtevi(self):
        from jsonschema.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate("AuthCheckRequest", {"scope_ref": "a", "permission": "b", "extra": 1})


class PreviewApplyTests(ImportBase):
    def test_sprememba_po_predogledu_zahteva_nov_predogled(self):
        self.apply()
        files = load()
        batch, result = importer.preview(files, SRC, self.actor)
        self.assertTrue(result.clean)
        pid = self.key("person", "staff-01")
        m.Person.objects.filter(pk=pid).update(display_name="Ročno spremenjeno")
        batch, result = importer.apply_batch(batch, files, self.actor)
        self.assertEqual(batch.status, m.ImportBatch.Status.REJECTED)
        self.assertIn("preview_stale", {p.code for p in result.problems})
        self.assertEqual(m.Person.objects.get(pk=pid).display_name, "Ročno spremenjeno")

    def test_sprememba_granta_po_predogledu(self):
        self.apply()
        files = load()
        batch, _ = importer.preview(files, SRC, self.actor)
        m.Grant.objects.update(valid_until=timezone.now() + timedelta(days=1))
        batch, result = importer.apply_batch(batch, files, self.actor)
        self.assertIn("preview_stale", {p.code for p in result.problems})

    def test_odvzem_pooblastila_uvoznika_po_predogledu(self):
        batch, _ = importer.preview(load(), SRC, self.actor)
        m.PersonRole.objects.filter(person=self.actor).delete()
        batch, result = importer.apply_batch(batch, load(), self.actor)
        self.assertIn("actor_not_authorized", {p.code for p in result.problems})
        self.assertFalse(m.Person.objects.exclude(pk=self.actor.pk).exists())

    def test_nespremenjen_predogled_se_uveljavi_in_ponovitev_ne_uspe(self):
        files = load()
        batch, _ = importer.preview(files, SRC, self.actor)
        batch, result = importer.apply_batch(batch, files, self.actor)
        self.assertEqual(batch.status, m.ImportBatch.Status.APPLIED)
        with self.assertRaises(ValueError):
            importer.apply_batch(batch, files, self.actor)

    def test_napaka_pred_koncnim_zapisom_ne_uveljavi_podatkov(self):
        files = load()
        batch, _ = importer.preview(files, SRC, self.actor)
        before = m.Person.objects.count()
        with (
            mock.patch.object(m.ImportBatch, "save", side_effect=RuntimeError("izpad")),
            self.assertRaises(RuntimeError),
        ):
            importer.apply_batch(batch, files, self.actor)
        self.assertEqual(m.Person.objects.count(), before)
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.FAILED)


class ConcurrentApplyTests(TransactionTestCase):
    """Sočasna uveljavitev iste serije v ločenih transakcijah PostgreSQL."""

    def test_samo_ena_uveljavitev_uspe(self):
        actor = m.Person.objects.create(display_name="Pooblaščeni")
        m.PersonRole.objects.create(person=actor, role=m.Role.OFFICE)
        files = load()
        batch, _ = importer.preview(files, SRC, actor)
        barrier = threading.Barrier(2)
        outcomes = []

        def worker():
            try:
                barrier.wait()
                importer.apply_batch(m.ImportBatch.objects.get(pk=batch.pk), files, actor)
                outcomes.append("applied")
            except ValueError:
                outcomes.append("rejected")
            finally:
                connection.close()

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(sorted(outcomes), ["applied", "rejected"])
        self.assertEqual(m.Relationship.objects.count(), 4)
        batch.refresh_from_db()
        self.assertEqual(batch.status, m.ImportBatch.Status.APPLIED)


class ProductionStubsGuard(ContractBase):
    def test_brez_debug_nadomestki_niso_dovoljeni(self):
        from config.checks import stubs_in_production

        self.assertTrue(stubs_in_production(False, {"m1"}))
        self.assertFalse(stubs_in_production(True, {"m1", "m2"}))
        self.assertFalse(stubs_in_production(False, set()))
