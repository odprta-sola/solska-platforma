"""Pogodbeni testi za osnutek D12 (api/openapi.yaml): P0 (pravi), M1 in M2 (nadomestka).

Vsak odgovor, ki gre skozi ContractBase.call ali scope_refs, se preveri proti operaciji v
pogodbi (status, vsebinski tip, shema s formati); glej contract_check. Klici neposredno prek
Django odjemalca drugje niso samodejno preverjeni. To so testi osnutka, ne potrditev D12.
"""

import hashlib
import json
from datetime import timedelta
from pathlib import Path

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import Resolver404, resolve
from django.utils import timezone

from registry import authz, services
from registry import models as m

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

    def class_of(self, username):
        return self.session(username).get(f"{P0}/me/classes").json()["classes"][0]["class_id"]

    def audience(self, author="staff-01", purpose="notice"):
        """Posnetek občinstva, ki ga ustvari prijavljeni avtor (seja)."""
        r = self.call(
            "post",
            f"{P0}/audiences/resolve",
            client=self.session(author),
            body={"class_id": self.class_of(author), "purpose": purpose},
        )
        self.assertEqual(r.status_code, 200, r.content)
        return r.json()

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
    """Predogled občinstva: uporabniški klic avtorja (seja, CSRF), shrani posnetek (D12)."""

    def resolve(self, author, class_id, purpose="notice", client=None):
        return self.call(
            "post",
            f"{P0}/audiences/resolve",
            client=client or self.session(author),
            body={"class_id": class_id, "purpose": purpose},
        )

    def test_avtor_dobi_prejemnike_svojega_oddelka(self):
        r = self.resolve("staff-01", self.class_of("staff-01"))
        self.assertEqual(r.status_code, 200)
        labels = {x["display_label"] for x in r.json()["recipients"]}
        self.assertEqual(
            labels, {"Starš Testni 01", "Starš Testni 02", "Starš Testni 03", "Starš Testni 04"}
        )
        text = r.content.decode()
        self.assertNotIn("example.invalid", text)  # brez kontaktov
        self.assertNotIn("email", text)

    def test_posnetek_je_shranjen_z_avtorjem_iz_seje(self):
        r = self.resolve("staff-01", self.class_of("staff-01")).json()
        snap = m.AudienceSnapshot.objects.get(ref=r["audience_ref"])
        self.assertEqual(snap.author, person_of("staff-01"))
        self.assertEqual(snap.permission, "acknowledge")
        members = {(str(x.person_id), x.scope_ref) for x in snap.members.all()}
        self.assertEqual(members, {(x["person_id"], x["scope_ref"]) for x in r["recipients"]})
        self.assertGreater(snap.expires_at, timezone.now())

    def test_avtorja_ni_mogoce_podtakniti(self):
        body = {"author_id": str(person_of("staff-01").pk), "class_id": "1", "purpose": "notice"}
        r = self.call("post", f"{P0}/audiences/resolve", client=self.session("staff-02"), body=body)
        self.assertEqual(r.status_code, 400)  # dodatno polje

    def test_zaposleni_zunaj_oddelka_zavrnjen(self):
        r = self.resolve("staff-02", self.class_of("staff-01"))
        self.assertEqual(r.status_code, 403)
        self.assertFalse(m.AudienceSnapshot.objects.exists())

    def test_obrazec_zahteva_drugo_dovoljenje(self):
        r = self.resolve("staff-01", self.class_of("staff-01"), purpose="form")
        self.assertEqual(r.json()["recipients"], [])  # seed ima samo acknowledge

    def test_odvzeta_povezava_izpade_iz_predogleda(self):
        authz.revoke_relationship(m.Relationship.objects.get(guardian=person_of("parent-02")))
        r = self.resolve("staff-01", self.class_of("staff-01"))
        self.assertNotIn("Starš Testni 02", {x["display_label"] for x in r.json()["recipients"]})

    def test_neznan_namen_ali_oddelek(self):
        self.assertEqual(
            self.resolve("staff-01", self.class_of("staff-01"), "kaj").status_code, 400
        )
        self.assertEqual(self.resolve("staff-01", "99999").status_code, 403)
        self.assertEqual(self.resolve("staff-01", "x").status_code, 403)

    def test_brez_seje_s_servisom_ali_brez_csrf(self):
        body = {"class_id": "1", "purpose": "notice"}
        self.assertEqual(self.call("post", f"{P0}/audiences/resolve", body=body).status_code, 401)
        r = self.call("post", f"{P0}/audiences/resolve", token=self.t_m1, body=body)
        self.assertEqual(r.status_code, 401)  # servis ne more predogledati v imenu avtorja
        self.assertEqual(self.resolve("parent-01", "1").status_code, 403)
        client = Client(enforce_csrf_checks=True)
        client.force_login(m.Account.objects.get(username="staff-01"))
        r = self.call("post", f"{P0}/audiences/resolve", client=client, body=body)
        self.assertEqual((r.status_code, r.json()["code"]), (403, "csrf_failed"))


class ContactContract(ContractBase):
    """Kontakt samo za prejemnika iz posnetka občinstva, z aktualnim upravičenjem (D12, C07)."""

    def setUp(self):
        super().setUp()
        self.aud = self.audience()

    def member(self, username):
        pid = str(person_of(username).pk)
        return next(x for x in self.aud["recipients"] if x["person_id"] == pid)

    def contact(self, username=None, token=None, client=None, **over):
        body = {"audience_ref": self.aud["audience_ref"]}
        if username:
            x = self.member(username)
            body.update(recipient_id=x["person_id"], scope_ref=x["scope_ref"])
        body.update(over)
        return self.call(
            "post",
            f"{P0}/delivery-contacts/resolve",
            token=None if client else (token or self.t_m1),
            client=client,
            body=body,
        )

    def assert_denied(self, r, status=403):
        self.assertEqual(r.status_code, status)
        validate("Error", r.json())
        self.assertNotIn("example.invalid", r.content.decode())

    def test_kontakt_za_prejemnika_iz_posnetka(self):
        r = self.contact("parent-01")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["email"], "family01@example.invalid")
        self.assertEqual(r.json()["locale"], "sl")

    def test_odsoten_kontakt_je_ocitno_stanje(self):
        r = self.contact("parent-04")
        self.assertEqual(r.json(), {"deliverable": False, "reason_code": "NO_CONTACT"})

    def test_brez_posnetka_ali_s_tujim_posnetkom(self):
        self.assert_denied(self.contact("parent-01", audience_ref="au_ugibam"))
        other = self.audience("staff-02")  # drug oddelek, drug posnetek
        theirs = {(r["person_id"], r["scope_ref"]) for r in other["recipients"]}
        x = next(
            r for r in self.aud["recipients"] if (r["person_id"], r["scope_ref"]) not in theirs
        )
        r = self.contact(
            audience_ref=other["audience_ref"],
            recipient_id=x["person_id"],
            scope_ref=x["scope_ref"],
        )
        self.assert_denied(r)

    def test_tuj_in_neobstojec_prejemnik_ali_sklic_enak_odgovor(self):
        x = self.member("parent-01")
        a = self.contact(recipient_id=str(person_of("staff-03").pk), scope_ref=x["scope_ref"])
        b = self.contact(recipient_id=x["person_id"], scope_ref="sr_ugibam")
        c = self.contact(recipient_id="ni-uuid", scope_ref=x["scope_ref"])
        for r in (a, b, c):
            self.assert_denied(r)
        self.assertEqual(
            {a.json()["code"], b.json()["code"], c.json()["code"]}, {"scope_not_allowed"}
        )

    def test_potekel_posnetek(self):
        m.AudienceSnapshot.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
        self.assert_denied(self.contact("parent-01"))

    def test_odvzem_po_posnetku(self):
        x = self.member("parent-02")
        authz.revoke_relationship(m.Relationship.objects.get(guardian=person_of("parent-02")))
        self.assert_denied(self.contact(recipient_id=x["person_id"], scope_ref=x["scope_ref"]))

    def test_upravicenje_mora_ustrezati_namenu_posnetka(self):
        """Posnetek za seznanitev: odločanje (decide) ne zadošča za kontakt."""
        p1 = person_of("parent-01")
        grant = m.Grant.objects.get(person=p1, scope_key=f"student:{person_of('student-01').pk}")
        m.Grant.objects.create(
            person=p1,
            scope_key=grant.scope_key,
            permission="decide",
            relationship=grant.relationship,
            approval=grant.approval,
            valid_from=grant.valid_from,
        )
        authz.revoke_grant(grant)
        x = self.member("parent-01")
        self.assert_denied(self.contact(recipient_id=x["person_id"], scope_ref=x["scope_ref"]))

    def test_samo_pooblascena_storitev(self):
        self.assert_denied(self.contact("parent-01", token=self.t_m2))
        self.assert_denied(self.contact("parent-01", token="svc_napacen"), 401)
        self.assert_denied(self.contact("parent-01", client=self.session("staff-01")), 401)
        m.ServiceClient.objects.filter(name="m1").update(active=False)
        self.assert_denied(self.contact("parent-01"), 401)


def delivery_body(parent_refs, key="k1", expires_at=None, **over):
    """Veljavna zahteva; pri opomniku ima vsaka postavka svoj need_ref (C09)."""
    reminder = over.get("kind", "reminder") == "reminder"
    body = {
        "idempotency_key": key,
        "event_key": f"ev-{key}",
        "kind": "reminder",
        "audience_ref": "au_test",
        "recipients": [
            {"person_id": pid, "scope_ref": ref, **({"need_ref": f"need-{n}"} if reminder else {})}
            for n, (pid, ref) in enumerate(parent_refs)
        ],
        "template_id": "m2.pending-response.v1",
        "params": {},
        "target": {"module": "M2", "resource_id": "form-demo-01"},
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

    def items(self, response):
        return {x["person_id"]: x["item_id"] for x in response.json()["recipients"]}

    def cancel(self, rid, item_ids, token=None):
        return self.call(
            "post",
            f"{M1}/delivery-requests/{rid}/cancel",
            token=token or self.t_m2,
            body={"item_ids": item_ids},
        )

    def advance(self, rid, item_id, new_state):
        self.call(
            "post",
            f"{M1}/_stub/advance",
            token=self.t_m2,
            body={"delivery_request_id": rid, "item_id": item_id, "state": new_state},
        )

    def test_prevzem_in_stanje(self):
        r = self.create()
        self.assertEqual(r.status_code, 202)
        rid = r.json()["delivery_request_id"]
        g = self.call("get", f"{M1}/delivery-requests/{rid}", token=self.t_m2)
        self.assertEqual(g.status_code, 200)
        self.assertEqual(g.json()["counts"], {"queued": 2})
        self.assertEqual(len(set(self.items(g).values())), 2)

    def test_idempotenca_in_konflikt(self):
        a, b = self.create(), self.create()
        self.assertEqual(a.json()["delivery_request_id"], b.json()["delivery_request_id"])
        self.assertEqual(self.items(a), self.items(b))
        c = self.create(template_id="drug")
        self.assertEqual(c.status_code, 409)

    def test_zahtevane_in_neveljavne_vrednosti(self):
        body = delivery_body(self.refs)
        del body["expires_at"]
        self.assertEqual(
            self.call("post", f"{M1}/delivery-requests", token=self.t_m2, body=body).status_code,
            400,
        )
        no_audience = delivery_body(self.refs, key="k1b")
        del no_audience["audience_ref"]
        self.assertEqual(
            self.call(
                "post", f"{M1}/delivery-requests", token=self.t_m2, body=no_audience
            ).status_code,
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
        r = self.create()
        rid, items = r.json()["delivery_request_id"], self.items(r)
        self.advance(rid, items[self.p2], "handed_off")
        res = self.cancel(rid, [items[self.p1], items[self.p2]])
        results = {x["item_id"]: x for x in res.json()["recipients"]}
        self.assertEqual(results[items[self.p1]]["cancel_result"], "cancelled_now")
        self.assertEqual(results[items[self.p2]]["cancel_result"], "too_late")
        self.assertEqual(results[items[self.p2]]["state"], "handed_off")
        again = self.cancel(rid, [items[self.p1]])
        self.assertEqual(again.json()["recipients"][0]["cancel_result"], "already_cancelled")

    def test_preklic_enega_ne_ustavi_drugih(self):
        r = self.create()
        rid, items = r.json()["delivery_request_id"], self.items(r)
        self.cancel(rid, [items[self.p1]])
        counts = self.call("get", f"{M1}/delivery-requests/{rid}", token=self.t_m2).json()["counts"]
        self.assertEqual(counts, {"cancelled": 1, "queued": 1})

    def test_rocno_nastavljen_iztek_je_koncno_stanje(self):
        """Stanje expired nastavi _stub/advance; samodejni iztek ni preizkušen (ni ga)."""
        r = self.create()
        rid, items = r.json()["delivery_request_id"], self.items(r)
        self.advance(rid, items[self.p1], "expired")
        res = self.cancel(rid, [items[self.p1]])
        self.assertEqual(res.json()["recipients"][0]["cancel_result"], "already_terminal")
        self.assertEqual(res.json()["recipients"][0]["state"], "expired")

    def test_preklic_neznane_postavke_in_prazen_izbor(self):
        rid = self.create().json()["delivery_request_id"]
        self.assertEqual(self.cancel(rid, ["di_nn"]).status_code, 404)
        self.assertEqual(self.cancel(rid, []).status_code, 400)

    def test_preklic_tuje_zahteve_je_404(self):
        r = self.create()
        rid, items = r.json()["delivery_request_id"], self.items(r)
        self.assertEqual(self.cancel(rid, [items[self.p1]], token=self.t_m2b).status_code, 404)


def issue_need(test, recipient_id, scope_ref, resource_id="form-demo-01", **extra):
    """need_ref iz nadomestka M2 za eno potrebo (C09)."""
    body = {"recipient_id": recipient_id, "scope_ref": scope_ref, "resource_id": resource_id}
    r = test.call("post", f"{M2}/_stub/needs", token=test.t_m1, body={**body, **extra})
    test.assertEqual(r.status_code, 200, r.content)
    return r.json()["need_ref"]


class ReminderCheckContract(ContractBase):
    def setUp(self):
        super().setUp()
        self.a = issue_need(self, "p", "s-otrok-a")
        self.b = issue_need(self, "p", "s-otrok-b")

    def check(self, need_ref, token=None, recipient_id="p", scope_ref="s-otrok-a"):
        return self.call(
            "post",
            f"{M2}/reminders/check",
            token=token or self.t_m1,
            body={"need_ref": need_ref, "recipient_id": recipient_id, "scope_ref": scope_ref},
        )

    def test_potreben_in_nepotreben(self):
        r = self.check(self.a)
        validate("ReminderCheckResponse", r.json())
        self.assertEqual(r.json(), {"needed": True, "reason_code": "REQUIRED"})
        self.call("post", f"{M2}/_stub/mark-done", token=self.t_m1, body={"need_ref": self.a})
        self.assertEqual(
            self.check(self.a).json(), {"needed": False, "reason_code": "NO_LONGER_REQUIRED"}
        )
        # odgovor za otroka A ne ustavi opomnika za otroka B (C09)
        self.assertTrue(self.check(self.b, scope_ref="s-otrok-b").json()["needed"])

    def test_tuj_neznan_ali_potekel_sklic_ni_nepotreben(self):
        past = (timezone.now() - timedelta(seconds=1)).isoformat()
        expired = issue_need(self, "p", "s-otrok-a", expires_at=past)
        for r in (
            self.check(self.b),  # sklic drugega obsega
            self.check(self.a, recipient_id="drug"),  # sklic druge osebe
            self.check("nd_neznan"),
            self.check(expired),
        ):
            self.assertEqual(r.status_code, 404)
            self.assertNotIn("needed", r.json())

    def test_napaka_ni_nepotreben(self):
        r = self.call("post", f"{M2}/reminders/check", token=self.t_m1, body={"need_ref": 1})
        self.assertEqual(r.status_code, 400)
        self.assertNotIn("needed", r.json())
        self.assertEqual(self.check(self.a, token=self.t_m2).status_code, 403)
        self.assertEqual(self.call("post", f"{M2}/reminders/check", body={}).status_code, 401)


class SpecCoverage(TestCase):
    def test_pogodba_je_zamrznjena_razlicica(self):
        """Sprememba api/openapi.yaml brez nove različice v api/zamrznitve.txt pade (C16)."""
        api = Path(__file__).resolve().parents[3] / "api"
        digest = hashlib.sha256((api / "openapi.yaml").read_bytes()).hexdigest()
        frozen = {}
        for line in (api / "zamrznitve.txt").read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                version, value = line.split()[:2]
                frozen[version] = value
        version = SPEC["info"]["version"]
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")  # brez »-osnutek«
        self.assertIn(version, frozen, "nova različica ni zapisana v api/zamrznitve.txt")
        self.assertEqual(frozen[version], digest, "pogodba se je spremenila brez nove različice")

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
