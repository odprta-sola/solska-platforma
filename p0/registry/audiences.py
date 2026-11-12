"""Posnetki občinstva (AudienceSnapshot): rok in čiščenje.

Posnetek je uporaben za razrešitev kontakta do ``expires_at`` (izključno); od tega trenutka ga
``delivery_binding`` ne vrne več. Potekle posnetke s člani vred izbriše ukaz
``purge_audience_snapshots``, ki ga zaganja storitev ``cleanup`` (vsako uro). Izbrisan in potekel
posnetek dajeta klicatelju enak odgovor. Rok (AUDIENCE_TTL v registry.api) je predlog D12/D07.
"""

from django.db import transaction
from django.utils import timezone

from . import models as m


def purge_expired(now=None):
    """Izbriše posnetke z ``expires_at <= now`` in njihove člane. Vrne število posnetkov."""
    now = now or timezone.now()
    with transaction.atomic():
        expired = m.AudienceSnapshot.objects.filter(expires_at__lte=now)
        m.AudienceMember.objects.filter(snapshot__in=expired).delete()
        count, _ = expired.delete()
    return count
