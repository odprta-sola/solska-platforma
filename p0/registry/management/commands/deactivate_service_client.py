"""Zajezitev: onemogoči servisni račun modula. Žeton takoj ne velja več (SECURITY.md)."""

from django.core.management.base import BaseCommand, CommandError

from registry import models as m


class Command(BaseCommand):
    help = "Onemogoči servisni račun modula (npr. ob izpostavljenem žetonu)."

    def add_arguments(self, parser):
        parser.add_argument("name")

    def handle(self, name, **options):
        if not m.ServiceClient.objects.filter(name=name).update(active=False):
            raise CommandError("Servisni račun ne obstaja.")
        self.stdout.write(f"Servisni račun {name} je onemogočen.")
