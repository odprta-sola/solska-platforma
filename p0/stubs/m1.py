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
from registry.services import error, service_only

from . import state

KINDS = {"notification", "reminder", "receipt", "change_notice"}
MAX_RECIPIENTS = 200  # predlog; končno mejo potrdi D12
TERMINAL = {"handed_off", "failed", "cancelled", "expired"}


def _is_str(v):
    return isinstance(v, str) and bool(v)


def _valid_request(body):
    if not all(_is_str(body.get(k)) for k in ("idempotency_key", "template_id", "locale")):
        return False
    if body.get("kind") not in KINDS or not isinstance(body.get("params", {}), dict):
        return False
    recipients = body.get("recipients")
    if not isinstance(recipients, list) or not 1 <= len(recipients) <= MAX_RECIPIENTS:
        return False
    for r in recipients:
        if (
            not isinstance(r, dict)
            or not _is_str(r.get("person_id"))
            or not _is_str(r.get("scope_ref"))
        ):
            return False
    target = body.get("target")
    if not isinstance(target, dict) or target.get("module") not in {"M1", "M2"}:
        return False
    if not _is_str(target.get("resource_id")):
        return False
    try:
        expires = datetime.fromisoformat(str(body.get("expires_at")).replace("Z", "+00:00"))
    except ValueError:
        return False
    return expires.tzinfo is not None and expires > timezone.now()


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
    if body is None or not _valid_request(body):
        return error(400, "invalid_request")
    fingerprint = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    key = (client.name, body["idempotency_key"])
    if key in state.IDEMPOTENCY:
        old_fp, old_id = state.IDEMPOTENCY[key]
        if old_fp != fingerprint:
            return error(409, "idempotency_conflict")
        return JsonResponse(_view(state.DELIVERIES[old_id]), status=202)
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
    ids = body.get("recipient_ids") if body else None
    if not isinstance(ids, list) or not ids or not all(_is_str(i) for i in ids):
        return error(400, "invalid_request")
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
