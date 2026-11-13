"""Nadomestek M2 (/m2/api/v1/): preverjanje potrebe po opomniku po pogodbi (D12, C09).

Potreba (need_ref) je sklic na eno konkretno potrebo: ena oseba, en obseg (otrok), en vir in
različica. Preverjanje vrne samo REQUIRED ali NO_LONGER_REQUIRED, nikoli vsebine odločitve.
Tuj, neznan ali potekel sklic je napaka 404, ne odgovor »nepotreben«.
"""

import secrets

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from registry.api import json_body
from registry.contract_schemas import parse_date_time, valid_request
from registry.services import error, service_only

from .models import StubNeed


def need_status(need_ref, recipient_id, scope_ref, at=None):
    """REQUIRED, NO_LONGER_REQUIRED ali None (sklic ne obstaja, je tuj ali potekel)."""
    at = at or timezone.now()
    need = StubNeed.objects.filter(
        need_ref=need_ref, recipient_id=recipient_id, scope_ref=scope_ref
    ).first()
    if need is None or (need.expires_at is not None and need.expires_at <= at):
        return None
    return "NO_LONGER_REQUIRED" if need.done else "REQUIRED"


@require_POST
@service_only("m2.reminders.check")
def reminder_check(request, client):
    body = json_body(request)
    if not valid_request("ReminderCheckRequest", body):
        return error(400, "invalid_request")
    status = need_status(body["need_ref"], body["recipient_id"], body["scope_ref"])
    if status is None:
        return error(404, "not_found")
    return JsonResponse({"needed": status == "REQUIRED", "reason_code": status})


@require_POST
@service_only("m2.reminders.check")
def stub_issue_need(request, client):
    """Samo nadomestek: izda need_ref za (prejemnik, obseg, vir, različica)."""
    body = json_body(request) or {}
    fields = ("recipient_id", "scope_ref", "resource_id")
    if not all(isinstance(body.get(f), str) and body[f] for f in fields):
        return error(400, "invalid_request")
    expires = body.get("expires_at")
    if expires is not None and parse_date_time(expires) is None:
        return error(400, "invalid_request")
    need = StubNeed.objects.create(
        need_ref="nd_" + secrets.token_urlsafe(12),
        version=body.get("version", 1) if isinstance(body.get("version", 1), int) else 1,
        expires_at=parse_date_time(expires) if expires else None,
        **{f: body[f] for f in fields},
    )
    return JsonResponse({"need_ref": need.need_ref})


@require_POST
@service_only("m2.reminders.check")
def stub_mark_done(request, client):
    """Samo nadomestek: označi potrebo za zaključeno (npr. starš je odgovoril)."""
    body = json_body(request) or {}
    if not isinstance(body.get("need_ref"), str):
        return error(400, "invalid_request")
    if not StubNeed.objects.filter(need_ref=body["need_ref"]).update(done=True):
        return error(404, "not_found")
    return JsonResponse({"ok": True})
