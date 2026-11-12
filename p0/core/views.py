from django.db import connection
from django.http import JsonResponse
from django.views import csrf
from django.views.decorators.http import require_GET

from .http import error, is_api


@require_GET
def health(request):
    """Preverjanje delovanja: ne vrača podatkov o osebah ali konfiguraciji."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception:  # noqa: BLE001 - napaka se ne razkrije odjemalcu
        return JsonResponse({"status": "unavailable"}, status=503)


def csrf_failure(request, reason=""):
    """Zavrnitev CSRF: na poteh API pogodbeni JSON 403, drugje privzeta stran Django."""
    if is_api(request):
        return error(403, "csrf_failed")
    return csrf.csrf_failure(request, reason=reason)
