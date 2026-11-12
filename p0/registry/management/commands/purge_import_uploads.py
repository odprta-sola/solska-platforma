"""Izbriše potekle začasne datoteke predogleda uvoza. Ponovljiv; zaganja ga storitev cleanup."""

from django.core.management.base import BaseCommand

from registry.uploads import purge_expired


class Command(BaseCommand):
    help = "Izbriše začasne datoteke predogledov uvoza, starejše od 24 ur."

    def handle(self, *args, **options):
        count = purge_expired()
        self.stdout.write(f"Počiščenih serij: {count}")
