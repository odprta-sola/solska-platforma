"""Servisna identiteta modulov in sklici na obsege (scope_ref).

Uporabniški klic uporablja sejo; servisni klic uporablja Bearer žeton modula in nikoli seje.
Žeton v prošnji ne pomeni prijave v imenu osebe (docs/arhitektura/vmesnik-P0-M1-M2.md).
"""

import hashlib
import secrets
from functools import wraps

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from core.http import error

from . import models as m


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
    """Vrne obstoječ ali nov neprosojen sklic za (oseba, obseg).

    get_or_create ob sočasni prvi zahtevi ujame kršitev enoličnosti in vrne že ustvarjeni sklic
    (namesto napake 500).
    """
    ref, created = m.ScopeRef.objects.get_or_create(
        person=person,
        scope_key=scope_key,
        defaults={
            "ref": "sr_" + secrets.token_urlsafe(16),
            "expires_at": expires_at,
            "issued_at": timezone.now(),
        },
    )
    if not created and ref.expires_at != expires_at:
        ref.expires_at = expires_at
        ref.save(update_fields=["expires_at"])
    return ref
