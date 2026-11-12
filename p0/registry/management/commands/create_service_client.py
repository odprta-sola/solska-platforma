"""Ustvari servisno identiteto modula. Žeton se izpiše enkrat; ne shranjujte ga v repozitorij."""

from django.core.management.base import BaseCommand, CommandError

from registry import models as m
from registry.services import create_service_client

KNOWN_SCOPES = {
    "p0.authorizations.check",
    "p0.audiences.resolve",
    "p0.contacts.resolve",
    "m1.delivery",
    "m2.reminders.check",
}


class Command(BaseCommand):
    help = "Ustvari servisni račun modula (npr. m1, m2) z omejenimi dovoljenji."

    def add_arguments(self, parser):
        parser.add_argument("name")
        parser.add_argument("--scope", action="append", required=True, dest="scopes")

    def handle(self, name, scopes, **options):
        unknown = set(scopes) - KNOWN_SCOPES
        if unknown:
            raise CommandError(f"Neznana dovoljenja: {sorted(unknown)}")
        if m.ServiceClient.objects.filter(name=name).exists():
            raise CommandError("Servisni račun že obstaja.")
        _, token = create_service_client(name, sorted(scopes))
        self.stdout.write(token)
