"""Nadomestek M2 (/m2/api/v1/): preverjanje potrebe po opomniku po pogodbi.

Vrne samo REQUIRED ali NO_LONGER_REQUIRED, nikoli vsebine odločitve.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from registry.api import json_body
from registry.services import error, service_only

from . import state


@require_POST
@service_only("m2.reminders.check")
def reminder_check(request, client):
    body = json_body(request)
    if body is None or not all(
        isinstance(body.get(k), str) and body.get(k)
        for k in ("need_ref", "recipient_id", "scope_ref")
    ):
        return error(400, "invalid_request")
    if body["need_ref"] in state.NEEDS_DONE:
        return JsonResponse({"needed": False, "reason_code": "NO_LONGER_REQUIRED"})
    return JsonResponse({"needed": True, "reason_code": "REQUIRED"})


@require_POST
@service_only("m2.reminders.check")
def stub_mark_done(request, client):
    """Samo nadomestek: označi potrebo za zaključeno."""
    body = json_body(request) or {}
    if not isinstance(body.get("need_ref"), str):
        return error(400, "invalid_request")
    state.NEEDS_DONE.add(body["need_ref"])
    return JsonResponse({"ok": True})
