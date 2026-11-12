"""Izbriše potekle posnetke občinstva in njihove člane. Ponovljiv; zaganja ga storitev cleanup."""

from django.core.management.base import BaseCommand

from registry.audiences import purge_expired


class Command(BaseCommand):
    help = "Izbriše posnetke občinstva, katerih rok je potekel, skupaj s člani."

    def handle(self, *args, **options):
        count = purge_expired()
        self.stdout.write(f"Počiščenih posnetkov: {count}")
