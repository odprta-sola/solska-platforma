"""Skupni odgovor z napako po pogodbi (api/openapi.yaml, shema Error)."""

import uuid

from django.http import JsonResponse

API_PREFIXES = ("/p0/api/", "/m1/api/", "/m2/api/")


def is_api(request):
    return request.path.startswith(API_PREFIXES)


def error(status, code, message=""):
    """Napaka po pogodbi: code, message, trace_id. Sporočilo ne razkriva tujih virov."""
    return JsonResponse(
        {"code": code, "message": message, "trace_id": uuid.uuid4().hex}, status=status
    )
