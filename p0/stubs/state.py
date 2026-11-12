"""Stanje nadomestkov v pomnilniku procesa. Samo za razvoj in pogodbene teste."""

DELIVERIES = {}  # delivery_request_id -> zapis
IDEMPOTENCY = {}  # (klicatelj, ključ) -> (odtis vsebine, delivery_request_id)
NEEDS_DONE = set()  # need_ref, ki jih M2 nadomestek šteje za zaključene


def reset():
    DELIVERIES.clear()
    IDEMPOTENCY.clear()
    NEEDS_DONE.clear()
