"""Začasne datoteke predogleda uvoza (ImportUpload): rok in čiščenje.

Pravilo: predogled je uporaben, dokler od najstarejše datoteke serije ne mine UPLOAD_RETENTION.
Od tega trenutka ga ni mogoče uveljaviti in datoteke se ob prvem dostopu izbrišejo; neodvisno od
dostopa jih izbriše ukaz ``purge_import_uploads``, ki ga zaganja storitev ``cleanup`` (vsako uro).
Ogled ali neuspešen poskus roka ne podaljša.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from . import models as m

UPLOAD_RETENTION = timedelta(hours=24)
PURGE_INTERVAL_SECONDS = 3600


def deadline(batch):
    """Trenutek, ko predogled poteče, ali None, če datotek ni."""
    first = batch.uploads.order_by("created_at").values_list("created_at", flat=True).first()
    return first + UPLOAD_RETENTION if first else None


def expired(batch, now=None):
    end = deadline(batch)
    return end is not None and (now or timezone.now()) >= end


def purge_expired(now=None):
    """Izbriše vse datoteke serij, katerih najstarejša datoteka je potekla. Vrne število serij."""
    cutoff = (now or timezone.now()) - UPLOAD_RETENTION
    with transaction.atomic():
        batch_ids = set(
            m.ImportUpload.objects.filter(created_at__lte=cutoff).values_list("batch_id", flat=True)
        )
        if batch_ids:
            m.ImportUpload.objects.filter(batch_id__in=batch_ids).delete()
    return len(batch_ids)
