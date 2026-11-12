"""Servisna identiteta modulov in sklici na obsege (scope_ref).

Uporabniški klic uporablja sejo; servisni klic uporablja Bearer žeton modula in nikoli seje.
Žeton v prošnji ne pomeni prijave v imenu osebe (docs/arhitektura/vmesnik-P0-M1-M2.md).
"""

import hashlib
import secrets
import uuid
from functools import wraps

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from . import models as m


def error(status, code, message=""):
    """Napaka po pogodbi: code, message, trace_id. Sporočilo ne razkriva tujih virov."""
    return JsonResponse(
        {"code": code, "message": message, "trace_id": uuid.uuid4().hex}, status=status
    )


def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def create_service_client(name, scopes):
    """Ustvari servisni račun; vrne (odjemalec, žeton). Žeton se vidi samo ob ustvarjanju."""
    token = "svc_" + secrets.token_urlsafe(32)
    client = m.ServiceClient.objects.create(name=name, token_hash=hash_token(token), scopes=scopes)
    return client, token


def service_client(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    return m.ServiceClient.objects.filter(
        token_hash=hash_token(header[7:].strip()), active=True
    ).first()


def service_only(scope):
    """Samo servisna identiteta z zahtevanim dovoljenjem. Seja se ne upošteva."""

    def decorator(view):
        @csrf_exempt  # ni piškotkov: CSRF ne velja za žeton v glavi
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            client = service_client(request)
            if client is None:
                return error(401, "invalid_service_identity")
            if scope not in client.scopes:
                return error(403, "service_scope_missing")
            return view(request, client, *args, **kwargs)

        return wrapper

    return decorator


def issue_scope_ref(person, scope_key, expires_at=None):
    """Vrne obstoječ ali nov neprosojen sklic za (oseba, obseg)."""
    existing = m.ScopeRef.objects.filter(person=person, scope_key=scope_key).first()
    if existing:
        if existing.expires_at != expires_at:
            existing.expires_at = expires_at
            existing.save(update_fields=["expires_at"])
        return existing
    return m.ScopeRef.objects.create(
        ref="sr_" + secrets.token_urlsafe(16),
        person=person,
        scope_key=scope_key,
        expires_at=expires_at,
        issued_at=timezone.now(),
    )
