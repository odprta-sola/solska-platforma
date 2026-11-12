"""Pogodbene napake API: vsak odgovor z napako na poteh API je JSON po shemi Error.

Nedosegljivost podatkovne zbirke je 503 (ne »ni dovoljeno«); nepričakovana napaka je 500
brez tehničnih podrobnosti. Sled se zapiše v dnevnik strežnika, ne v odgovor.
"""

import logging

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.db import DatabaseError
from django.http import Http404

from .http import error, is_api

log = logging.getLogger("p0.api")

CONVERT = {404: "not_found", 405: "method_not_allowed"}


class ApiErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            is_api(request)
            and response.status_code in CONVERT
            and not response.get("Content-Type", "").startswith("application/json")
        ):
            converted = error(response.status_code, CONVERT[response.status_code])
            if response.has_header("Allow"):
                converted["Allow"] = response["Allow"]
            return converted
        return response

    def process_exception(self, request, exception):
        if not is_api(request) or isinstance(
            exception, (Http404, PermissionDenied, SuspiciousOperation)
        ):
            return None
        if isinstance(exception, DatabaseError):
            log.exception("Nedosegljiva evidenca")
            return error(503, "temporarily_unavailable")
        log.exception("Nepričakovana napaka API")
        return error(500, "internal_error")
