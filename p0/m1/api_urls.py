"""Strežniški API M1 po pogodbi 1.0.0 (/m1/api/v1/). Izdela ekipa M1.

Usmerjen je samo, ko nadomestek M1 ni vklopljen (STUBS brez m1). Pot in sheme so v
api/openapi.yaml; nadomestek p0/stubs/m1.py je referenca obnašanja:

- POST delivery-requests              (202 po trajnem zapisu; idempotenca, event_key)
- GET  delivery-requests/<id>         (stanja in reason_code po postavkah)
- POST delivery-requests/<id>/cancel  (selektivni preklic po item_id)
"""

urlpatterns = []
