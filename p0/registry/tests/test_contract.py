"""Pogodbeni testi za osnutek D12 (api/openapi.yaml): P0 (pravi), M1 in M2 (nadomestka).

Vsak odgovor, ki gre skozi ContractBase.call ali scope_refs, se preveri proti operaciji v
pogodbi (status, vsebinski tip, shema s formati); glej contract_check. Klici neposredno prek
Django odjemalca drugje niso samodejno preverjeni. To so testi osnutka, ne potrditev D12.
"""

import json
from datetime import timedelta
from unittest import mock

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import Resolver404, resolve
from django.utils import timezone

from registry import authz, services
from registry import models as m
from stubs import state

from .contract_check import SPEC, check, validate

P0, M1, M2 = "/p0/api/v1", "/m1/api/v1", "/m2/api/v1"


def person_of(key):
    mp = m.SourceMapping.objects.get(source_key=key, entity_type="person")
    return m.Person.objects.get(pk=mp.target_id)


class ContractBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_test_data", verbosity=0)
        _, cls.t_m1 = services.create_service_client(
            "m1",
            [
                "p0.audiences.resolve",
                "p0.authorizations.check",
                "p0.contacts.resolve",
                "m2.reminders.check",
            ],
        )
        _, cls.t_m2 = services.create_service_client(
            "m2", ["m1.delivery", "p0.authorizations.check"]
        )
        _, cls.t_m2b = services.create_service_client("m2-drug", ["m1.delivery"])

    def setUp(self):
        state.reset()

    def call(self, method, path, token=None, body=None, client=None, **extra):
        client = client or Client()
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
        data = json.dumps(body) if body is not None else None
        response = getattr(client, method)(
            path, data=data, content_type="application/json", **headers, **extra
        )
        return check(method, path, response)

    def session(self, username):
        client = Client()
        client.force_login(m.Account.objects.get(username=username))
        return client

    def scope_refs(self, username):
        """scope_ref-i staršev iz GET /me/relationships (po imenu otroka)."""
        path = f"{P0}/me/relationships"
        data = check("get", path, self.session(username).get(path)).json()
        return {r["student_display_name"]: r["scopes"] for r in data["relationships"]}

    def ref(self, username, student_name, permission="m1.confirm"):
        scopes = self.scope_refs(username)[student_name]
        return next(s["scope_ref"] for s in scopes if s["permission"] == permission)


class UserEndpointsContract(ContractBase):
    def test_odgovori_ustrezajo_shemam(self):
        parent = self.session("parent-01")
        validate("Me", parent.get(f"{P0}/me").json())
        validate("Relationships", parent.get(f"{P0}/me/relationships").json())
        validate("Classes", self.session("staff-01").get(f"{P0}/me/classes").json())

    def test_napake_ustrezajo_shemi(self):
        for response in (Client().get(f"{P0}/me"), self.call("post", f"{P0}/audiences/resolve")):
            validate("Error", response.json())

    def test_sklici_so_neprosojni_in_ne_vsebujejo_ID_otroka(self):
        refs = self.scope_refs("parent-01")
        for scopes in refs.values():
            for s in scopes:
                self.assertTrue(s["scope_ref"].startswith("sr_"))
                self.assertNotIn(str(person_of("student-01").pk), s["scope_ref"])


class AuthorizationCheckContract(ContractBase):
    def check_as_user(self, username, scope_ref, permission="m1.confirm", client=None, **body):
        client = client or self.session(username)
        return self.call(
            "post",
            f"{P0}/authorizations/check",
            client=client,
            body={"scope_ref": scope_ref, "permission": permission, **body},
        )

    def test_lastni_obseg_dovoljen(self):
        ref = self.ref("parent-01", "Učenec Testni 01")
        r = self.check_as_user("parent-01", ref)
        self.assertEqual(r.status_code, 200)
        validate("AuthCheckResponse", r.json())
        self.assertEqual(r.json()["reason_code"], "ALLOWED")

    def test_tuj_in_ugiban_sklic_enako_zavrnjena(self):
        tuj = self.ref("parent-01", "Učenec Testni 01")
        a = self.check_as_user("parent-03", tuj).json()
        b = self.check_as_user("parent-03", "sr_ugibam").json()
        self.assertFalse(a["allowed"])
        self.assertEqual(a["reason_code"], b["reason_code"])
        self.assertEqual(a["reason_code"], "NOT_ALLOWED")

    def test_neznano_dovoljenje_ni_dovoljeno(self):
        ref = self.ref("parent-01", "Učenec Testni 01")
        self.assertFalse(self.check_as_user("parent-01", ref, "m1.vse").json()["allowed"])

    def test_dovoljenje_se_ne_prenasa_med_dejanji(self):
        ref = self.ref("parent-01", "Učenec Testni 01")  # ima samo acknowledge
        self.assertFalse(self.check_as_user("parent-01", ref, "m2.decide").json()["allowed"])

    def test_tuj_subject_id_403(self):
        ref = self.ref("parent-01", "Učenec Testni 01")
        r = self.check_as_user("parent-01", ref, subject_id=str(person_of("parent-03").pk))
        self.assertEqual(r.status_code, 403)
        validate("Error", r.json())

    def test_neveljavna_zahteva_400(self):
        client = self.session("parent-01")
        r = self.call("post", f"{P0}/authorizations/check", client=client, body={"scope_ref": 1})
        self.assertEqual(r.status_code, 400)
        r = self.call("post", f"{P0}/authorizations/check", client=client, body=[1])
        self.assertEqual(r.status_code, 400)

    def test_seja_brez_csrf_zavrnjena(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(m.Account.objects.get(username="parent-01"))
        r = self.call(
            "post",
            f"{P0}/authorizations/check",
            client=client,
            body={"scope_ref": "x", "permission": "m1.confirm"},
        )
        self.assertEqual(r.status_code, 403)

    def test_odvzem_povezave_in_upravicenja_prevlada(self):
        ref = self.ref("parent-02", "Učenec Testni 01")
        self.assertTrue(self.check_as_user("parent-02", ref).json()["allowed"])
        authz.revoke_relationship(m.Relationship.objects.get(guardian=person_of("parent-02")))
        self.assertFalse(self.check_as_user("parent-02", ref).json()["allowed"])
        ref1 = self.ref("parent-01", "Učenec Testni 01")
        scope = f"student:{person_of('student-01').pk}"
        authz.revoke_grant(m.Grant.objects.get(person=person_of("parent-01"), scope_key=scope))
        self.assertFalse(self.check_as_user("parent-01", ref1).json()["allowed"])
        self.assertTrue(
            self.check_as_user("parent-01", self.ref("parent-01", "Učenec Testni 02")).json()[
                "allowed"
            ]
        )

    def test_odvzem_pusti_sled(self):
        rel = m.Relationship.objects.get(guardian=person_of("parent-02"))
        authz.revoke_relationship(rel, actor=person_of("staff-03"), source="test")
        audit = m.ChangeAudit.objects.get(action="relationship.revoked")
        self.assertEqual(audit.entity_id, str(rel.pk))
        self.assertEqual(m.Relationship.objects.count(), 5)  # zapis ostane

    def test_potecen_sklic_je_neaktiven(self):
        ref = self.ref("parent-01", "Učenec Testni 01")
        m.ScopeRef.objects.filter(ref=ref).update(expires_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(
            self.check_as_user("parent-01", ref).json()["reason_code"], "SCOPE_INACTIVE"
        )

    def test_servisni_klic(self):
        ref = self.ref("parent-01", "Učenec Testni 01")
        body = {
            "subject_id": str(person_of("parent-01").pk),
            "scope_ref": ref,
            "permission": "m1.confirm",
        }
        r = self.call("post", f"{P0}/authorizations/check", token=self.t_m2, body=body)
        self.assertEqual(r.status_code, 200)
        validate("AuthCheckResponse", r.json())
        self.assertTrue(r.json()["allowed"])
        # brez subject_id ni mogoče
        no_subject = {k: v for k, v in body.items() if k != "subject_id"}
        self.assertEqual(
            self.call(
                "post", f"{P0}/authorizations/check", token=self.t_m2, body=no_subject
            ).status_code,
            400,
        )
        # tuj subject s tujim sklicem
        other = {**body, "subject_id": str(person_of("parent-03").pk)}
        self.assertFalse(
            self.call("post", f"{P0}/authorizations/check", token=self.t_m2, body=other).json()[
                "allowed"
            ]
        )

    def test_servisni_klic_zahteva_zeton_in_dovoljenje(self):
        body = {"subject_id": "x", "scope_ref": "x", "permission": "m1.confirm"}
        # neveljaven žeton ne preide na sejo, tudi če je ta prisotna
        client = self.session("parent-01")
        r = self.call(
            "post", f"{P0}/authorizations/check", client=client, token="svc_napacen", body=body
        )
        self.assertEqual(r.status_code, 401)
        r = self.call("post", f"{P0}/authorizations/check", token=self.t_m2b, body=body)
        self.assertEqual(r.status_code, 403)
        m.ServiceClient.objects.filter(name="m2").update(active=False)
        r = self.call("post", f"{P0}/authorizations/check", token=self.t_m2, body=body)
        self.assertEqual(r.status_code, 401)


class AudiencesContract(ContractBase):
    def class_id(self, username):
        return self.session(username).get(f"{P0}/me/classes").json()["classes"][0]["class_id"]

    def resolve(self, author, class_id, purpose="notice", token=None):
        return self.call(
            "post",
            f"{P0}/audiences/resolve",
            token=token or self.t_m1,
            body={"author_id": str(person_of(author).pk), "class_id": class_id, "purpose": purpose},
        )

    def test_avtor_dobi_prejemnike_svojega_oddelka(self):
        r = self.resolve("staff-01", self.class_id("staff-01"))
        self.assertEqual(r.status_code, 200)
        validate("AudienceResponse", r.json())
        labels = {x["display_label"] for x in r.json()["recipients"]}
        self.assertEqual(
            labels, {"Starš Testni 01", "Starš Testni 02", "Starš Testni 03", "Starš Testni 04"}
        )
        text = r.content.decode()
        self.assertNotIn("example.invalid", text)  # brez kontaktov
        self.assertNotIn("email", text)

    def test_zaposleni_zunaj_oddelka_zavrnjen(self):
        r = self.resolve("staff-02", self.class_id("staff-01"))
        self.assertEqual(r.status_code, 403)
        validate("Error", r.json())

    def test_obrazec_zahteva_drugo_dovoljenje(self):
        r = self.resolve("staff-01", self.class_id("staff-01"), purpose="form")
        self.assertEqual(r.json()["recipients"], [])  # seed ima samo acknowledge

    def test_odvzeta_povezava_izpade_iz_predogleda(self):
        authz.revoke_relationship(m.Relationship.objects.get(guardian=person_of("parent-02")))
        r = self.resolve("staff-01", self.class_id("staff-01"))
        self.assertNotIn("Starš Testni 02", {x["display_label"] for x in r.json()["recipients"]})

    def test_neznan_namen_ali_oddelek(self):
        self.assertEqual(
            self.resolve("staff-01", self.class_id("staff-01"), "kaj").status_code, 400
        )
        self.assertEqual(self.resolve("staff-01", "99999").status_code, 403)
        self.assertEqual(self.resolve("staff-01", "x").status_code, 403)

    def test_brez_zetona_ali_dovoljenja(self):
        body = {"author_id": "x", "class_id": "1", "purpose": "notice"}
        self.assertEqual(self.call("post", f"{P0}/audiences/resolve", body=body).status_code, 401)
        self.assertEqual(
            self.call("post", f"{P0}/audiences/resolve", token=self.t_m2b, body=body).status_code,
            403,
        )


class ContactContract(ContractBase):
    """Pravila upravičenosti ob simulirani preverjeni vezavi na dostavo (mehanizem: D12)."""

    def setUp(self):
        super().setUp()
        patcher = mock.patch("registry.api.delivery_binding_verified", return_value=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def contact(self, username, student, token=None, ref=None):
        ref = ref or self.ref(username, student)
        return self.call(
            "post",
            f"{P0}/delivery-contacts/resolve",
            token=token or self.t_m1,
            body={
                "recipient_id": str(person_of(username).pk),
                "scope_ref": ref,
                "delivery_request_id": "dr_test",
            },
        )

    def test_kontakt_za_upravicenega(self):
        r = self.contact("parent-01", "Učenec Testni 01")
        self.assertEqual(r.status_code, 200)
        validate("ContactResponse", r.json())
        self.assertEqual(r.json()["email"], "family01@example.invalid")

    def test_odsoten_kontakt_je_ocitno_stanje(self):
        r = self.contact("parent-04", "Učenec Testni 04")
        self.assertEqual(r.json(), {"deliverable": False, "reason_code": "NO_CONTACT"})

    def test_tuj_sklic_ali_odvzeta_povezava_zavrnjena(self):
        tuj = self.ref("parent-01", "Učenec Testni 01")
        r = self.contact("parent-03", "", ref=tuj)
        self.assertEqual(r.status_code, 403)
        validate("Error", r.json())
        ref = self.ref("parent-02", "Učenec Testni 01")
        authz.revoke_relationship(m.Relationship.objects.get(guardian=person_of("parent-02")))
        self.assertEqual(self.contact("parent-02", "", ref=ref).status_code, 403)

    def test_samo_pooblascena_storitev(self):
        self.assertEqual(
            self.contact("parent-01", "Učenec Testni 01", token=self.t_m2).status_code, 403
        )
        body = {"recipient_id": "x", "scope_ref": "y", "delivery_request_id": "z"}
        # seja ni dovolj
        client = self.session("staff-01")
        self.assertEqual(
            self.call(
                "post", f"{P0}/delivery-contacts/resolve", client=client, body=body
            ).status_code,
            401,
        )

    def test_ugibanje_ne_razkrije_kontaktov(self):
        for bad in ("sr_a", "", "x"):
            r = self.call(
                "post",
                f"{P0}/delivery-contacts/resolve",
                token=self.t_m1,
                body={
                    "recipient_id": str(person_of("parent-01").pk),
                    "scope_ref": bad,
                    "delivery_request_id": "dr",
                },
            )
            self.assertIn(r.status_code, (400, 403))
            self.assertNotIn("example.invalid", r.content.decode())


class ContactBindingContract(ContractBase):
    """Brez preverljive vezave na dostavo P0 kontakta ne vrne, ne glede na vhod."""

    def resolve(self, body, token=None, client=None):
        return self.call(
            "post",
            f"{P0}/delivery-contacts/resolve",
            token=token if client is None else None,
            client=client,
            body=body,
        )

    def body(self, username="parent-01", student="Učenec Testni 01", request_id="dr_x"):
        return {
            "recipient_id": str(person_of(username).pk),
            "scope_ref": self.ref(username, student),
            "delivery_request_id": request_id,
        }

    def assert_no_contact(self, r, status):
        self.assertEqual(r.status_code, status)
        self.assertEqual(r["Content-Type"], "application/json")
        validate("Error", r.json())
        self.assertNotIn("example.invalid", r.content.decode())
        self.assertNotIn("email", r.json())

    def test_veljaven_prejemnik_brez_preverjene_vezave(self):
        for rid in ("dr_x", "dr_" + "0" * 16, "x"):
            self.assert_no_contact(self.resolve(self.body(request_id=rid), self.t_m1), 503)

    def test_odsoten_kontakt_ni_razkrit_pred_preverjanjem(self):
        r = self.resolve(self.body("parent-04", "Učenec Testni 04"), self.t_m1)
        self.assert_no_contact(r, 503)

    def test_tuj_in_neobstojec_sklic_enak_odgovor(self):
        tuj = self.body()
        tuj["recipient_id"] = str(person_of("parent-03").pk)
        neobstojec = {**self.body(), "scope_ref": "sr_ugibam"}
        a, b = self.resolve(tuj, self.t_m1), self.resolve(neobstojec, self.t_m1)
        self.assert_no_contact(a, 503)
        self.assert_no_contact(b, 503)
        self.assertEqual(a.json()["code"], b.json()["code"])

    def test_odvzem_pred_razresitvijo(self):
        body = self.body("parent-02", "Učenec Testni 01")
        authz.revoke_relationship(m.Relationship.objects.get(guardian=person_of("parent-02")))
        self.assert_no_contact(self.resolve(body, self.t_m1), 503)

    def test_neupravicen_napacen_ali_neaktiven_zeton_in_seja(self):
        body = self.body()
        self.assert_no_contact(self.resolve(body, self.t_m2), 403)
        self.assert_no_contact(self.resolve(body, "svc_napacen"), 401)
        self.assert_no_contact(self.resolve(body, None), 401)
        self.assert_no_contact(self.resolve(body, client=self.session("staff-01")), 401)
        m.ServiceClient.objects.filter(name="m1").update(active=False)
        self.assert_no_contact(self.resolve(body, self.t_m1), 401)


def delivery_body(parent_refs, key="k1", expires_at=None, **over):
    body = {
        "idempotency_key": key,
        "kind": "reminder",
        "recipients": [{"person_id": pid, "scope_ref": ref} for pid, ref in parent_refs],
        "template_id": "m2.pending-response.v1",
        "locale": "sl",
        "params": {},
        "target": {"module": "M2", "resource_id": "form-demo-01"},
        "need_ref": "need-demo-001",
        "expires_at": expires_at
        or (timezone.now() + timedelta(days=1)).isoformat().replace("+00:00", "Z"),
    }
    body.update(over)
    return body


class DeliveryStubContract(ContractBase):
    def setUp(self):
        super().setUp()
        self.expires = (timezone.now() + timedelta(days=1)).isoformat().replace("+00:00", "Z")
        self.p1, self.p2 = str(person_of("parent-01").pk), str(person_of("parent-02").pk)
        self.refs = [
            (self.p1, self.ref("parent-01", "Učenec Testni 01")),
            (self.p2, self.ref("parent-02", "Učenec Testni 01")),
        ]

    def create(self, token=None, **kw):
        kw.setdefault("expires_at", self.expires)
        return self.call(
            "post",
            f"{M1}/delivery-requests",
            token=token or self.t_m2,
            body=delivery_body(self.refs, **kw),
        )

    def test_prevzem_in_stanje(self):
        r = self.create()
        self.assertEqual(r.status_code, 202)
        validate("DeliveryStatus", r.json())
        rid = r.json()["delivery_request_id"]
        g = self.call("get", f"{M1}/delivery-requests/{rid}", token=self.t_m2)
        self.assertEqual(g.status_code, 200)
        validate("DeliveryStatus", g.json())
        self.assertEqual(g.json()["counts"], {"queued": 2})

    def test_idempotenca_in_konflikt(self):
        a, b = self.create(), self.create()
        self.assertEqual(a.json()["delivery_request_id"], b.json()["delivery_request_id"])
        c = self.create(template_id="drug")
        self.assertEqual(c.status_code, 409)
        validate("Error", c.json())

    def test_zahtevane_in_neveljavne_vrednosti(self):
        body = delivery_body(self.refs)
        del body["expires_at"]
        self.assertEqual(
            self.call("post", f"{M1}/delivery-requests", token=self.t_m2, body=body).status_code,
            400,
        )
        past = (timezone.now() - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
        self.assertEqual(self.create(key="k2", expires_at=past).status_code, 400)
        self.assertEqual(self.create(key="k3", kind="sms").status_code, 400)
        self.assertEqual(
            self.create(key="k4", target={"module": "X", "resource_id": "a"}).status_code, 400
        )
        self.assertEqual(self.create(key="k5", recipients=[]).status_code, 400)

    def test_klicoci_vidi_samo_svoje(self):
        rid = self.create().json()["delivery_request_id"]
        other = services.create_service_client("m2-tretji", ["m1.delivery"])[1]
        self.assertEqual(
            self.call("get", f"{M1}/delivery-requests/{rid}", token=other).status_code, 404
        )
        self.assertEqual(self.call("get", f"{M1}/delivery-requests/{rid}").status_code, 401)

    def test_selektivni_preklic_in_delna_stanja(self):
        rid = self.create().json()["delivery_request_id"]
        self.call(
            "post",
            f"{M1}/_stub/advance",
            token=self.t_m2,
            body={"delivery_request_id": rid, "person_id": self.p2, "state": "handed_off"},
        )
        r = self.call(
            "post",
            f"{M1}/delivery-requests/{rid}/cancel",
            token=self.t_m2,
            body={"recipient_ids": [self.p1, self.p2]},
        )
        validate("CancelResponse", r.json())
        results = {x["person_id"]: x for x in r.json()["recipients"]}
        self.assertEqual(results[self.p1]["cancel_result"], "cancelled_now")
        self.assertEqual(results[self.p2]["cancel_result"], "too_late")
        self.assertEqual(results[self.p2]["state"], "handed_off")
        again = self.call(
            "post",
            f"{M1}/delivery-requests/{rid}/cancel",
            token=self.t_m2,
            body={"recipient_ids": [self.p1]},
        )
        self.assertEqual(again.json()["recipients"][0]["cancel_result"], "already_cancelled")

    def test_preklic_enega_ne_ustavi_drugih(self):
        rid = self.create().json()["delivery_request_id"]
        self.call(
            "post",
            f"{M1}/delivery-requests/{rid}/cancel",
            token=self.t_m2,
            body={"recipient_ids": [self.p1]},
        )
        counts = self.call("get", f"{M1}/delivery-requests/{rid}", token=self.t_m2).json()["counts"]
        self.assertEqual(counts, {"cancelled": 1, "queued": 1})

    def test_rocno_nastavljen_iztek_je_koncno_stanje(self):
        """Stanje expired nastavi _stub/advance; samodejni iztek ni preizkušen (ni ga)."""
        rid = self.create().json()["delivery_request_id"]
        self.call(
            "post",
            f"{M1}/_stub/advance",
            token=self.t_m2,
            body={"delivery_request_id": rid, "person_id": self.p1, "state": "expired"},
        )
        r = self.call(
            "post",
            f"{M1}/delivery-requests/{rid}/cancel",
            token=self.t_m2,
            body={"recipient_ids": [self.p1]},
        )
        self.assertEqual(r.json()["recipients"][0]["cancel_result"], "already_terminal")
        self.assertEqual(r.json()["recipients"][0]["state"], "expired")

    def test_preklic_neznanega_prejemnika_in_prazen_izbor(self):
        rid = self.create().json()["delivery_request_id"]
        url = f"{M1}/delivery-requests/{rid}/cancel"
        self.assertEqual(
            self.call("post", url, token=self.t_m2, body={"recipient_ids": ["nn"]}).status_code, 404
        )
        self.assertEqual(
            self.call("post", url, token=self.t_m2, body={"recipient_ids": []}).status_code, 400
        )

    def test_preklic_tuje_zahteve_je_404(self):
        rid = self.create().json()["delivery_request_id"]
        r = self.call(
            "post",
            f"{M1}/delivery-requests/{rid}/cancel",
            token=self.t_m2b,
            body={"recipient_ids": [self.p1]},
        )
        self.assertEqual(r.status_code, 404)  # tuja zahteva


class ReminderCheckContract(ContractBase):
    def check(self, need_ref="need-1", token=None):
        return self.call(
            "post",
            f"{M2}/reminders/check",
            token=token or self.t_m1,
            body={"need_ref": need_ref, "recipient_id": "p", "scope_ref": "s"},
        )

    def test_potreben_in_nepotreben(self):
        r = self.check()
        validate("ReminderCheckResponse", r.json())
        self.assertEqual(r.json(), {"needed": True, "reason_code": "REQUIRED"})
        self.call("post", f"{M2}/_stub/mark-done", token=self.t_m1, body={"need_ref": "need-1"})
        self.assertEqual(
            self.check().json(), {"needed": False, "reason_code": "NO_LONGER_REQUIRED"}
        )
        self.assertTrue(self.check("need-2").json()["needed"])  # selektivno

    def test_napaka_ni_nepotreben(self):
        r = self.call("post", f"{M2}/reminders/check", token=self.t_m1, body={"need_ref": 1})
        self.assertEqual(r.status_code, 400)
        self.assertNotIn("needed", r.json())
        self.assertEqual(self.check(token=self.t_m2).status_code, 403)
        self.assertEqual(self.call("post", f"{M2}/reminders/check", body={}).status_code, 401)


class SpecCoverage(TestCase):
    def test_vsaka_pot_iz_specifikacije_je_usmerjena(self):
        for path in SPEC["paths"]:
            try:
                resolve(path.replace("{id}", "abc"))
            except Resolver404:
                self.fail(f"Pot {path} iz openapi.yaml nima pogleda")

    def test_vse_operacije_imajo_varnostno_shemo_in_napake(self):
        for path, ops in SPEC["paths"].items():
            for method, op in ops.items():
                self.assertIn("security", op, f"{method} {path}")
                self.assertIn("401", op["responses"], f"{method} {path}")
