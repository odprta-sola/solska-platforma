"""D12, točke B v pogodbi in nadomestkih (sprejel tehnični nosilec 13. 11. 2026).

Vsak razred preveri eno točko z nasprotnim primerom iz priprave odločitev (C03, C06, C08–C11,
C13). Časi obdelave so relativni glede na zdaj, da testi ne zastarajo.
"""

from datetime import datetime, time, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

from django.db import DatabaseError, IntegrityError, transaction
from django.utils import timezone

from registry import authz
from registry import models as m
from stubs import m1 as stub_m1
from stubs.models import StubDelivery, StubItem

from .test_contract import M1, ContractBase, issue_need, person_of

TZ = ZoneInfo("Europe/Ljubljana")


def iso(value):
    return value.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z")


def local(day, hour, minute=0):
    return datetime.combine(day, time(hour, minute), TZ)


def next_weekday(weekday, after_days=7):
    """Datum naslednjega dneva v tednu (0 = ponedeljek) vsaj `after_days` od danes."""
    day = timezone.now().astimezone(TZ).date() + timedelta(days=after_days)
    return day + timedelta(days=(weekday - day.weekday()) % 7)


class StubBase(ContractBase):
    def setUp(self):
        super().setUp()
        self.aud = self.audience()  # 7. a: starši 01, 02, 03, 04
        self.by_person = {}
        for r in self.aud["recipients"]:
            self.by_person.setdefault(r["person_id"], r["scope_ref"])
        self.p = {k: str(person_of(k).pk) for k in ("parent-01", "parent-02", "parent-03")}
        self.p4 = str(person_of("parent-04").pk)

    def item(self, key, **extra):
        pid = self.p.get(key) or self.p4
        return {"person_id": pid, "scope_ref": self.by_person[pid], **extra}

    def body(self, items, key="k", event="ev-1", kind="notification", expires=None, **over):
        return {
            "idempotency_key": key,
            "event_key": event,
            "kind": kind,
            "audience_ref": self.aud["audience_ref"],
            "recipients": items,
            "template_id": "m1.notice.v1",
            "params": {},
            "target": {"module": "M1", "resource_id": "obvestilo-1"},
            "expires_at": iso(expires or timezone.now() + timedelta(days=20)),
            **over,
        }

    def create(self, body, token=None):
        return self.call("post", f"{M1}/delivery-requests", token=token or self.t_m2, body=body)

    def process(self, rid, at=None):
        body = {"delivery_request_id": rid, **({"at": iso(at)} if at else {})}
        r = self.call("post", f"{M1}/_stub/process", token=self.t_m2, body=body)
        self.assertEqual(r.status_code, 200, r.content)
        return r

    def status(self, rid):
        r = self.call("get", f"{M1}/delivery-requests/{rid}", token=self.t_m2)
        return {x["person_id"]: (x["state"], x["reason_code"]) for x in r.json()["recipients"]}

    def weekday_noon(self):
        return local(next_weekday(1), 12)  # torek opoldne, znotraj urnika


class DurabilityTests(StubBase):
    """C11: 202 šele po trajnem zapisu; brez zapisa 503 in nič delno prevzetega."""

    def test_izpad_pri_zapisu_postavk(self):
        body = self.body([self.item("parent-01"), self.item("parent-02")])
        with mock.patch.object(StubItem.objects, "bulk_create", side_effect=DatabaseError):
            r = self.create(body)
        self.assertEqual(r.status_code, 503)
        self.assertFalse(StubDelivery.objects.exists())
        again = self.create(body)  # ponovitev po izpadu
        self.assertEqual(again.status_code, 202)
        self.assertEqual(StubDelivery.objects.count(), 1)
        self.assertEqual(StubItem.objects.count(), 2)

    def test_stanje_je_v_bazi(self):
        rid = self.create(self.body([self.item("parent-01")])).json()["delivery_request_id"]
        self.assertTrue(StubDelivery.objects.filter(id=rid).exists())


class IdempotencyWindowTests(StubBase):
    """C08: okno ponovitve 30 dni in poslovni ključ dogodka."""

    def test_okno_ponovitve(self):
        body = self.body([self.item("parent-01")], expires=timezone.now() + timedelta(days=40))
        first = self.create(body)
        accepted = StubDelivery.objects.get().accepted_at
        with mock.patch("stubs.m1.timezone.now", return_value=accepted + timedelta(days=29)):
            same = self.create(body)
        with mock.patch("stubs.m1.timezone.now", return_value=accepted + timedelta(days=30)):
            late = self.create(body)
        self.assertEqual(same.status_code, 202)
        self.assertEqual(same.json()["delivery_request_id"], first.json()["delivery_request_id"])
        self.assertEqual((late.status_code, late.json()["code"]), (409, "replay_window_expired"))

    def test_nov_kljuc_ne_podvoji_dogodka(self):
        self.create(self.body([self.item("parent-01")], key="a"))
        dup = self.create(self.body([self.item("parent-02"), self.item("parent-01")], key="b"))
        self.assertEqual((dup.status_code, dup.json()["code"]), (409, "duplicate_event"))
        self.assertEqual(StubItem.objects.count(), 1)  # brez delnega prevzema
        other = self.create(self.body([self.item("parent-02")], key="c"))
        self.assertEqual(other.status_code, 202)  # isti dogodek, nova postavka
        nxt = self.create(self.body([self.item("parent-01")], key="d", event="ev-2"))
        self.assertEqual(nxt.status_code, 202)  # naslednji načrtovani opomnik

    def test_dogodek_je_lociran_po_klicatelju(self):
        self.create(self.body([self.item("parent-01")], key="a"))
        r = self.create(self.body([self.item("parent-01")], key="a"), token=self.t_m2b)
        self.assertEqual(r.status_code, 202)

    def test_baza_varuje_poslovni_kljuc(self):
        self.create(self.body([self.item("parent-01")], key="a"))
        first = StubItem.objects.get()
        with self.assertRaises(IntegrityError), transaction.atomic():
            StubItem.objects.create(
                item_id="di_x",
                delivery=first.delivery,
                position=1,
                owner=first.owner,
                event_key=first.event_key,
                person_id=first.person_id,
                scope_ref=first.scope_ref,
            )


class NeedRefTests(StubBase):
    """C09: need_ref na postavko; ena potreba ne ustavi druge; napaka ni »nepotreben«."""

    def reminder(self, needs, key="r"):
        items = [self.item(k, need_ref=n) for k, n in needs.items()]
        return self.create(self.body(items, key=key, event=f"ev-{key}", kind="reminder"))

    def test_need_ref_samo_pri_opomniku(self):
        no_need = self.create(self.body([self.item("parent-01")], kind="reminder"))
        self.assertEqual(no_need.status_code, 400)
        extra = self.create(self.body([self.item("parent-01", need_ref="nd_x")], key="n2"))
        self.assertEqual(extra.status_code, 400)

    def test_selektivna_potreba(self):
        a = issue_need(self, self.p["parent-01"], self.by_person[self.p["parent-01"]])
        b = issue_need(self, self.p["parent-03"], self.by_person[self.p["parent-03"]])
        rid = self.reminder({"parent-01": a, "parent-03": b}).json()["delivery_request_id"]
        self.call("post", "/m2/api/v1/_stub/mark-done", token=self.t_m1, body={"need_ref": a})
        self.process(rid, self.weekday_noon())
        st = self.status(rid)
        self.assertEqual(st[self.p["parent-01"]], ("cancelled", "NO_LONGER_REQUIRED"))
        self.assertEqual(st[self.p["parent-03"]], ("handed_off", None))

    def test_neznana_potreba_zadrzi(self):
        rid = self.reminder({"parent-01": "nd_neznan"}).json()["delivery_request_id"]
        self.process(rid, self.weekday_noon())
        self.assertEqual(self.status(rid)[self.p["parent-01"]], ("held", "CHECK_UNAVAILABLE"))

    def test_m2_izklopljen_zadrzi(self):
        a = issue_need(self, self.p["parent-01"], self.by_person[self.p["parent-01"]])
        rid = self.reminder({"parent-01": a}).json()["delivery_request_id"]
        with self.settings(STUBS={"m1"}):
            self.process(rid, self.weekday_noon())
        self.assertEqual(self.status(rid)[self.p["parent-01"]], ("held", "CHECK_UNAVAILABLE"))


class AuthorizationAtActionTests(StubBase):
    """C06: odvzem med čakanjem zadrži dostavo samo prizadete postavke."""

    def test_odvzem_med_cakanjem(self):
        rid = self.create(self.body([self.item("parent-01"), self.item("parent-02")])).json()[
            "delivery_request_id"
        ]
        rel = m.Relationship.objects.get(guardian=person_of("parent-02"))
        authz.revoke_relationship(rel)
        self.process(rid, self.weekday_noon())
        st = self.status(rid)
        self.assertEqual(st[self.p["parent-02"]], ("held", "NOT_ALLOWED"))
        self.assertEqual(st[self.p["parent-01"]], ("handed_off", None))

    def test_brez_kontakta_papirna_pot(self):
        rid = self.create(self.body([self.item("parent-04")])).json()["delivery_request_id"]
        self.process(rid, self.weekday_noon())
        self.assertEqual(self.status(rid)[self.p4], ("held", "NO_CONTACT"))


class QuietHoursTests(StubBase):
    """C10: M1 je lastnik urnika (osnutek: delavniki 7–20, Europe/Ljubljana)."""

    def test_petek_zvecer_z_iztekom_pred_ponedeljkom(self):
        friday = next_weekday(4)
        rid = self.create(
            self.body([self.item("parent-01")], expires=local(friday + timedelta(days=1), 12))
        ).json()["delivery_request_id"]
        self.process(rid, local(friday, 20, 30))
        self.assertEqual(
            self.status(rid)[self.p["parent-01"]], ("expired", "DELIVERY_WINDOW_EXPIRED")
        )

    def test_tihi_cas_nato_dostava(self):
        friday = next_weekday(4)
        monday = friday + timedelta(days=3)
        rid = self.create(self.body([self.item("parent-01")], expires=local(monday, 12))).json()[
            "delivery_request_id"
        ]
        self.process(rid, local(friday, 21))
        self.assertEqual(self.status(rid)[self.p["parent-01"]], ("queued", "QUIET_HOURS"))
        self.process(rid, local(monday, 6, 59))
        self.assertEqual(self.status(rid)[self.p["parent-01"]], ("queued", "QUIET_HOURS"))
        self.process(rid, local(monday, 7))
        self.assertEqual(self.status(rid)[self.p["parent-01"]], ("handed_off", None))

    def test_ob_izteku_ni_predaje(self):
        noon = self.weekday_noon()
        rid = self.create(self.body([self.item("parent-01")], expires=noon)).json()[
            "delivery_request_id"
        ]
        self.process(rid, noon)
        self.assertEqual(
            self.status(rid)[self.p["parent-01"]], ("expired", "DELIVERY_WINDOW_EXPIRED")
        )

    def test_meje_urnika_in_poletni_cas(self):
        nxt = stub_m1.next_delivery_time
        tuesday = next_weekday(1)
        self.assertEqual(nxt(local(tuesday, 7)), local(tuesday, 7))
        self.assertEqual(nxt(local(tuesday, 20)), local(tuesday + timedelta(days=1), 7))
        # sobota pred prehodom na poletni čas (29. 3. 2026) -> ponedeljek 7.00 CEST = 5.00 UTC
        spring = nxt(datetime(2026, 3, 28, 21, 0, tzinfo=ZoneInfo("UTC")))
        self.assertEqual(iso(spring), "2026-03-30T05:00:00Z")
        # petek pred prehodom na zimski čas (25. 10. 2026) -> ponedeljek 7.00 CET = 6.00 UTC
        autumn = nxt(datetime(2026, 10, 23, 19, 0, tzinfo=ZoneInfo("UTC")))
        self.assertEqual(iso(autumn), "2026-10-26T06:00:00Z")


class LanguageTests(StubBase):
    """C03: jezik prejemnika iz P0; brez tihe zamenjave, izrecna preglasitev na postavki."""

    def test_manjkajoc_prevod_zadrzi(self):
        m.Person.objects.filter(pk=self.p["parent-01"]).update(preferred_language="it")
        rid = self.create(self.body([self.item("parent-01"), self.item("parent-03")])).json()[
            "delivery_request_id"
        ]
        self.process(rid, self.weekday_noon())
        st = self.status(rid)
        self.assertEqual(st[self.p["parent-01"]], ("held", "TRANSLATION_MISSING"))
        self.assertEqual(st[self.p["parent-03"]], ("handed_off", None))

    def test_preglasitev_na_postavki(self):
        m.Person.objects.filter(pk=self.p["parent-01"]).update(preferred_language="it")
        rid = self.create(self.body([self.item("parent-01", locale="sl")])).json()[
            "delivery_request_id"
        ]
        self.process(rid, self.weekday_noon())
        self.assertEqual(self.status(rid)[self.p["parent-01"]], ("handed_off", None))

    def test_skupnega_jezika_ni(self):
        r = self.create(self.body([self.item("parent-01")], locale="sl"))
        self.assertEqual(r.status_code, 400)


class UncertainHandoffTests(StubBase):
    """C13: negotova predaja ostane zadržana do ročne odločitve; preklic ni lažen uspeh."""

    def setUp(self):
        super().setUp()
        r = self.create(self.body([self.item("parent-01"), self.item("parent-03")]))
        self.rid = r.json()["delivery_request_id"]
        self.items = {x["person_id"]: x["item_id"] for x in r.json()["recipients"]}
        for pid in self.items:
            self.advance(pid, "held", "HANDOFF_UNCERTAIN")

    def advance(self, pid, state, reason=""):
        body = {"delivery_request_id": self.rid, "item_id": self.items[pid], "state": state}
        return self.call(
            "post", f"{M1}/_stub/advance", token=self.t_m2, body={**body, "reason_code": reason}
        )

    def test_obdelava_ne_ponovi_sama(self):
        self.process(self.rid, self.weekday_noon())
        self.assertEqual(self.status(self.rid)[self.p["parent-01"]], ("held", "HANDOFF_UNCERTAIN"))

    def test_preklic_in_rocna_ponovitev(self):
        p1, p3 = self.p["parent-01"], self.p["parent-03"]
        r = self.call(
            "post",
            f"{M1}/delivery-requests/{self.rid}/cancel",
            token=self.t_m2,
            body={"item_ids": [self.items[p1]]},
        )
        self.assertEqual(r.json()["recipients"][0]["cancel_result"], "too_late")
        self.assertEqual(r.json()["recipients"][0]["state"], "held")
        self.assertEqual(self.advance(p1, "queued").status_code, 409)  # po preklicu ni ponovitve
        self.assertEqual(self.advance(p3, "queued").status_code, 200)  # ročna odločitev
        self.process(self.rid, self.weekday_noon())
        self.assertEqual(self.status(self.rid)[p3], ("handed_off", None))

    def test_iztek_ohrani_razlog_negotovosti(self):
        expires = StubDelivery.objects.get().expires_at
        self.process(self.rid, expires)
        self.assertEqual(
            self.status(self.rid)[self.p["parent-01"]], ("expired", "HANDOFF_UNCERTAIN")
        )
