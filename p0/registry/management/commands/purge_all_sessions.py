"""Zajezitev: izbriše vse seje in s tem odjavi vse uporabnike (SECURITY.md).

Sledi sprememb in vpogledov (ChangeAudit, AccessAudit) ostanejo. Za izbris samo poteklih sej
uporabite Djangov `clearsessions`.
"""

from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Izbriše vse seje (odjavi vse uporabnike); sledi ostanejo."

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="potrditev brez vprašanja")

    def handle(self, yes, **options):
        if not yes:
            self.stderr.write("Za izbris vseh sej dodajte --yes.")
            return
        count, _ = Session.objects.all().delete()
        self.stdout.write(f"Izbrisanih sej: {count}.")
