"""Trajni zapisi nadomestkov M1/M2 (D12, C11). Samo za razvoj in pogodbene teste.

Pravi moduli imajo svoje tabele; P0 jih ne bere. Nadomestek hrani zahteve v bazi, da 202 sledi
trajnemu zapisu in da stanje preživi ponovni zagon procesa.
"""

from django.db import models
from django.utils import timezone


class StubDelivery(models.Model):
    """Prevzeta zahteva za dostavo (M1)."""

    id = models.CharField(primary_key=True, max_length=32)
    owner = models.CharField(max_length=64)  # ime servisnega klicatelja
    idempotency_key = models.CharField(max_length=256)
    fingerprint = models.CharField(max_length=64)
    event_key = models.CharField(max_length=256)
    kind = models.CharField(max_length=16)
    audience_ref = models.CharField(max_length=256)
    template_id = models.CharField(max_length=256)
    params = models.JSONField(default=dict)  # vsebina za predlogo; potrebna za dostavo po obnovi
    target = models.JSONField(default=dict)  # ciljni modul in vir (npr. module, resource_id)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "idempotency_key"], name="uniq_stub_idem")
        ]


class StubItem(models.Model):
    """Postavka dostave: (oseba, scope_ref) z lastnim item_id in razlogom stanja."""

    item_id = models.CharField(primary_key=True, max_length=32)
    delivery = models.ForeignKey(StubDelivery, on_delete=models.CASCADE, related_name="items")
    position = models.PositiveIntegerField()
    owner = models.CharField(max_length=64)
    event_key = models.CharField(max_length=256)
    person_id = models.CharField(max_length=256)
    scope_ref = models.CharField(max_length=256)
    need_ref = models.CharField(max_length=256, blank=True)
    locale = models.CharField(max_length=16, blank=True)
    state = models.CharField(max_length=16, default="queued")
    reason_code = models.CharField(max_length=32, blank=True)
    no_retry = models.BooleanField(default=False)  # po preklicu negotove predaje

    class Meta:
        ordering = ["position"]
        constraints = [
            # Poslovna deduplikacija (C08): isti dogodek za isto postavko le enkrat na klicatelja.
            models.UniqueConstraint(
                fields=["owner", "event_key", "person_id", "scope_ref"], name="uniq_stub_event"
            )
        ]


class StubNeed(models.Model):
    """Potreba po odzivu v M2: ena oseba, en obseg, en vir in različica (C09)."""

    need_ref = models.CharField(primary_key=True, max_length=64)
    recipient_id = models.CharField(max_length=256)
    scope_ref = models.CharField(max_length=256)
    resource_id = models.CharField(max_length=256)
    version = models.PositiveIntegerField(default=1)
    done = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
