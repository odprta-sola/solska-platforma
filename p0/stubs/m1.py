"""Nadomestek M1 (/m1/api/v1/): iste sheme kot pogodba, brez pošiljanja e-pošte.

Izvede pravila D12, točke B (sprejel tehnični nosilec 13. 11. 2026, potrditev mentorjev odprta):

- C11: 202 šele po trajnem zapisu zahteve in postavk v bazi (ena transakcija).
- C08: isti idempotency_key in vsebina vrneta isti prevzem do IDEMPOTENCY_WINDOW po prevzemu,
  nato 409 replay_window_expired; drugačna vsebina 409 idempotency_conflict. Poslovni ključ
  (klicatelj, event_key, oseba, obseg) se ne ponovi: nov ključ za isti dogodek je 409
  duplicate_event, brez delnega prevzema.
- C09: pri opomniku ima vsaka postavka svoj need_ref.
- C06, C10, C13, C03: obdelava (_stub/process) ob času `at` ponovno preveri rok, tihi čas,
  upravičenje, potrebo, kontakt in jezik; razlog stanja je viden v reason_code.

Pot /_stub/* ni del pogodbe. Nadomestek kliče P0 in M2 v istem procesu prek istih funkcij, ki jih
uporabljata njuna API (poenostavitev nadomestka); pravi M1 kliče API (C05).
"""

import hashlib
import json
import uuid
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import DatabaseError, IntegrityError, transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from registry.api import delivery_contact, json_body
from registry.contract_schemas import parse_date_time, valid_request
from registry.services import error, service_only

from . import m2
from .models import StubDelivery, StubItem

TERMINAL = {"handed_off", "failed", "cancelled", "expired"}
IDEMPOTENCY_WINDOW = timedelta(days=30)  # C08, predlog: hramba ključa za ponovitve
SCHOOL_TZ = ZoneInfo("Europe/Ljubljana")
DELIVERY_HOURS = (time(7), time(20))  # C10, osnutek: delavniki 7–20, ne potrjen urnik šole
TEMPLATE_LOCALES = {"sl"}  # nadomestek: vse predloge obstajajo samo v slovenščini (D05 odprt)
# Zadržanja, ki jih obdelava sama ponovno presodi; HANDOFF_UNCERTAIN zahteva ročno odločitev.
RECHECK = {"NOT_ALLOWED", "NO_CONTACT", "TRANSLATION_MISSING", "CHECK_UNAVAILABLE"}


def _expires(body):
    """Rok dostave po RFC 3339 (kot v pogodbi) ali None."""
    return parse_date_time(body["expires_at"])


def _invalid(body):
    """Koda napake neveljavne zahteve ali None. Pogoj roka preveri klicatelj."""
    if not valid_request("DeliveryRequest", body) or _expires(body) is None:
        return "invalid_request"
    pairs = [(r["person_id"], r["scope_ref"]) for r in body["recipients"]]
    if len(pairs) != len(set(pairs)):
        return "duplicate_recipient"  # ista postavka (oseba, obseg) dvakrat
    reminder = body["kind"] == "reminder"
    if any(("need_ref" in r) != reminder for r in body["recipients"]):
        return "invalid_request"  # need_ref je obvezen pri opomniku in samo pri njem (C09)
    return None


def _view(delivery):
    items = list(delivery.items.all())
    counts = {}
    for item in items:
        counts[item.state] = counts.get(item.state, 0) + 1
    return {
        "delivery_request_id": delivery.id,
        "state": "queued" if any(i.state == "queued" for i in items) else "processed",
        "recipients": [
            {
                "item_id": i.item_id,
                "person_id": i.person_id,
                "scope_ref": i.scope_ref,
                "state": i.state,
                "reason_code": i.reason_code or None,
            }
            for i in items
        ],
        "counts": counts,
    }


def _replay(existing, fingerprint, now):
    if now >= existing.accepted_at + IDEMPOTENCY_WINDOW:
        return error(409, "replay_window_expired")
    if existing.fingerprint != fingerprint:
        return error(409, "idempotency_conflict")
    return JsonResponse(_view(existing), status=202)


@require_POST
@service_only("m1.delivery")
def create_delivery(request, client):
    body = json_body(request)
    problem = _invalid(body)
    if problem:
        return error(400, problem)
    now = timezone.now()
    fingerprint = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    key = {"owner": client.name, "idempotency_key": body["idempotency_key"]}
    existing = StubDelivery.objects.filter(**key).first()
    if existing:
        return _replay(existing, fingerprint, now)
    if _expires(body) <= now:
        return error(400, "invalid_request")
    pairs = {(r["person_id"], r["scope_ref"]) for r in body["recipients"]}
    seen = StubItem.objects.filter(owner=client.name, event_key=body["event_key"])
    if any((i.person_id, i.scope_ref) in pairs for i in seen):
        return error(409, "duplicate_event")
    try:
        with transaction.atomic():
            delivery = StubDelivery.objects.create(
                id="dr_" + uuid.uuid4().hex[:16],
                fingerprint=fingerprint,
                event_key=body["event_key"],
                kind=body["kind"],
                audience_ref=body["audience_ref"],
                template_id=body["template_id"],
                expires_at=_expires(body),
                accepted_at=now,
                **key,
            )
            StubItem.objects.bulk_create(
                StubItem(
                    item_id="di_" + uuid.uuid4().hex[:16],
                    delivery=delivery,
                    position=n,
                    owner=client.name,
                    event_key=body["event_key"],
                    person_id=r["person_id"],
                    scope_ref=r["scope_ref"],
                    need_ref=r.get("need_ref", ""),
                    locale=r.get("locale", ""),
                )
                for n, r in enumerate(body["recipients"])
            )
    except IntegrityError:
        existing = StubDelivery.objects.filter(**key).first()  # sočasna ista zahteva
        if existing:
            return _replay(existing, fingerprint, now)
        return error(409, "duplicate_event")
    except DatabaseError:
        return error(503, "unavailable")  # brez trajnega zapisa ni 202 (C11)
    return JsonResponse(_view(delivery), status=202)


def _own(client, delivery_request_id):
    return StubDelivery.objects.filter(id=delivery_request_id, owner=client.name).first()


@require_GET
@service_only("m1.delivery")
def get_delivery(request, client, delivery_request_id):
    delivery = _own(client, delivery_request_id)
    if delivery is None:
        return error(404, "not_found")
    return JsonResponse(_view(delivery))


@require_POST
@service_only("m1.delivery")
def cancel_delivery(request, client, delivery_request_id):
    delivery = _own(client, delivery_request_id)
    if delivery is None:
        return error(404, "not_found")
    body = json_body(request)
    if not valid_request("CancelRequest", body):
        return error(400, "invalid_request")
    ids = list(dict.fromkeys(body["item_ids"]))
    with transaction.atomic():
        items = {i.item_id: i for i in delivery.items.select_for_update().filter(item_id__in=ids)}
        if len(items) != len(ids):
            return error(404, "not_found")
        results = []
        for item_id in ids:
            item = items[item_id]
            if item.state == "held" and item.reason_code == "HANDOFF_UNCERTAIN":
                # Sporočilo je morda že predano; brez lažnega uspeha in brez nove ponovitve (C13).
                item.no_retry, outcome = True, "too_late"
            elif item.state in ("queued", "held"):
                item.state, outcome = "cancelled", "cancelled_now"
            elif item.state == "cancelled":
                outcome = "already_cancelled"
            elif item.state == "handed_off":
                outcome = "too_late"
            else:
                outcome = "already_terminal"
            item.save(update_fields=["state", "no_retry"])
            results.append(
                {
                    "item_id": item_id,
                    "person_id": item.person_id,
                    "state": item.state,
                    "cancel_result": outcome,
                }
            )
    return JsonResponse({"delivery_request_id": delivery.id, "recipients": results})


def next_delivery_time(at):
    """Prvi dovoljeni trenutek dostave ob `at` ali pozneje (UTC), po urniku šole (C10)."""
    local = at.astimezone(SCHOOL_TZ)
    for offset in range(8):
        day = local.date() + timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        start = datetime.combine(day, DELIVERY_HOURS[0], SCHOOL_TZ)
        end = datetime.combine(day, DELIVERY_HOURS[1], SCHOOL_TZ)
        if local < start:
            return start.astimezone(at.tzinfo)
        if local < end:
            return at
    raise AssertionError("urnik brez dovoljenega časa")


def _set(item, state, reason=""):
    item.state, item.reason_code = state, reason
    item.save(update_fields=["state", "reason_code"])


def _process_item(delivery, item, at):
    """En korak obdelave postavke ob času `at` (vrstni red je del pravila D12, točke B)."""
    uncertain = item.reason_code == "HANDOFF_UNCERTAIN"
    if at >= delivery.expires_at:
        return _set(
            item, "expired", "HANDOFF_UNCERTAIN" if uncertain else "DELIVERY_WINDOW_EXPIRED"
        )
    if uncertain:
        return None  # samo ročna odločitev (C13)
    if next_delivery_time(at) != at:
        if next_delivery_time(at) >= delivery.expires_at:
            return _set(item, "expired", "DELIVERY_WINDOW_EXPIRED")
        return _set(item, "queued", "QUIET_HOURS")
    contact = delivery_contact(delivery.audience_ref, item.person_id, item.scope_ref, at)
    if contact is None:
        return _set(item, "held", "NOT_ALLOWED")  # odvzem med čakanjem zadrži dostavo (C06)
    if delivery.kind == "reminder":
        need = (
            m2.need_status(item.need_ref, item.person_id, item.scope_ref, at)
            if "m2" in settings.STUBS
            else None
        )
        if need is None:
            return _set(item, "held", "CHECK_UNAVAILABLE")  # napaka ni »nepotreben«
        if need == "NO_LONGER_REQUIRED":
            return _set(item, "cancelled", "NO_LONGER_REQUIRED")
    if not contact["deliverable"]:
        return _set(item, "held", "NO_CONTACT")  # papirna pot
    if (item.locale or contact["locale"]) not in TEMPLATE_LOCALES:
        return _set(item, "held", "TRANSLATION_MISSING")  # brez tihe zamenjave jezika (C03)
    return _set(item, "handed_off")


@require_POST
@service_only("m1.delivery")
def stub_process(request, client):
    """Samo nadomestek: obdela čakajoče postavke zahteve ob času `at` (privzeto zdaj)."""
    body = json_body(request) or {}
    delivery = _own(client, body.get("delivery_request_id"))
    at = parse_date_time(body["at"]) if "at" in body else timezone.now()
    if delivery is None or at is None:
        return error(400, "invalid_request")
    with transaction.atomic():
        for item in delivery.items.select_for_update():
            held = item.reason_code in RECHECK | {"HANDOFF_UNCERTAIN"}
            if item.state == "queued" or (item.state == "held" and held):
                _process_item(delivery, item, at)
    return JsonResponse(_view(delivery))


@require_POST
@service_only("m1.delivery")
def stub_advance(request, client):
    """Samo nadomestek: ročno nastavi stanje postavke (npr. negotova predaja ali odločitev)."""
    body = json_body(request) or {}
    delivery = _own(client, body.get("delivery_request_id"))
    new_state, reason = body.get("state"), body.get("reason_code", "")
    item = delivery.items.filter(item_id=body.get("item_id")).first() if delivery else None
    if item is None or new_state not in TERMINAL | {"held", "queued"}:
        return error(400, "invalid_request")
    if new_state == "queued":
        # Ponovitev po negotovi predaji je izrecna ročna odločitev in ne velja po preklicu.
        if item.reason_code != "HANDOFF_UNCERTAIN" or item.no_retry:
            return error(409, "retry_not_allowed")
    _set(item, new_state, reason if isinstance(reason, str) else "")
    return JsonResponse({"ok": True})
