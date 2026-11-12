from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health(request):
    """Preverjanje delovanja: ne vrača podatkov o osebah ali konfiguraciji."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception:  # noqa: BLE001 - napaka se ne razkrije odjemalcu
        return JsonResponse({"status": "unavailable"}, status=503)
