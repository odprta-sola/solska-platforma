"""Nadomestek M1 (/m1/api/v1/): iste sheme kot pogodba, brez pošiljanja.

Ne pošilja e-pošte. Stanja prejemnikov premika ukaz _stub/advance, da je mogoče
preizkusiti preklic ob handed_off, expired in failed.
"""

import hashlib
import json
import uuid
from datetime import datetime

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from registry.api import json_body
from registry.contract_schemas import valid_request
from registry.services import error, service_only

from . import state

TERMINAL = {"handed_off", "failed", "cancelled", "expired"}


def _expires(body):
    """Rok dostave kot datum s časovnim pasom ali None."""
    try:
        expires = datetime.fromisoformat(body["expires_at"].replace("Z", "+00:00"))
    except ValueError:
        return None
    return expires if expires.tzinfo is not None else None


def _invalid(body):
    """Koda napake neveljavne zahteve ali None. Pogoj roka preveri klicatelj."""
    if not valid_request("DeliveryRequest", body) or _expires(body) is None:
        return "invalid_request"
    ids = [r["person_id"] for r in body["recipients"]]
    if len(ids) != len(set(ids)):
        return "duplicate_recipient"  # identiteta postavke ni določena v D12
    return None


def _view(record):
    counts = {}
    for r in record["recipients"].values():
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    return {
        "delivery_request_id": record["id"],
        "state": "queued"
        if any(r["state"] == "queued" for r in record["recipients"].values())
        else "processed",
        "recipients": [
            {"person_id": pid, "state": r["state"]} for pid, r in record["recipients"].items()
        ],
        "counts": counts,
    }


@require_POST
@service_only("m1.delivery")
def create_delivery(request, client):
    body = json_body(request)
    problem = _invalid(body)
    if problem:
        return error(400, problem)
    fingerprint = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    key = (client.name, body["idempotency_key"])
    if key in state.IDEMPOTENCY:
        old_fp, old_id = state.IDEMPOTENCY[key]
        if old_fp != fingerprint:
            return error(409, "idempotency_conflict")
        return JsonResponse(_view(state.DELIVERIES[old_id]), status=202)
    if _expires(body) <= timezone.now():
        return error(400, "invalid_request")
    record = {
        "id": "dr_" + uuid.uuid4().hex[:16],
        "owner": client.name,
        "recipients": {
            r["person_id"]: {"state": "queued", "scope_ref": r["scope_ref"]}
            for r in body["recipients"]
        },
    }
    state.DELIVERIES[record["id"]] = record
    state.IDEMPOTENCY[key] = (fingerprint, record["id"])
    return JsonResponse(_view(record), status=202)


def _own(client, delivery_request_id):
    record = state.DELIVERIES.get(delivery_request_id)
    return record if record and record["owner"] == client.name else None


@require_GET
@service_only("m1.delivery")
def get_delivery(request, client, delivery_request_id):
    record = _own(client, delivery_request_id)
    if record is None:
        return error(404, "not_found")
    return JsonResponse(_view(record))


@require_POST
@service_only("m1.delivery")
def cancel_delivery(request, client, delivery_request_id):
    record = _own(client, delivery_request_id)
    if record is None:
        return error(404, "not_found")
    body = json_body(request)
    if not valid_request("CancelRequest", body):
        return error(400, "invalid_request")
    ids = body["recipient_ids"]
    if any(i not in record["recipients"] for i in ids):
        return error(404, "not_found")
    results = []
    for pid in dict.fromkeys(ids):
        r = record["recipients"][pid]
        if r["state"] in ("queued", "held"):
            r["state"], outcome = "cancelled", "cancelled_now"
        elif r["state"] == "cancelled":
            outcome = "already_cancelled"
        elif r["state"] == "handed_off":
            outcome = "too_late"
        else:
            outcome = "already_terminal"
        results.append({"person_id": pid, "state": r["state"], "cancel_result": outcome})
    return JsonResponse({"delivery_request_id": record["id"], "recipients": results})


@require_POST
@service_only("m1.delivery")
def stub_advance(request, client):
    """Samo nadomestek: premakne stanje prejemnika (npr. v handed_off ali expired)."""
    body = json_body(request) or {}
    record = _own(client, body.get("delivery_request_id"))
    new_state = body.get("state")
    pid = body.get("person_id")
    if record is None or pid not in record["recipients"] or new_state not in TERMINAL | {"held"}:
        return error(400, "invalid_request")
    record["recipients"][pid]["state"] = new_state
    return JsonResponse({"ok": True})
