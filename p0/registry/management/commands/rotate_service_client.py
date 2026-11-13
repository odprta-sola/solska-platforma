"""Zajezitev: izda nov žeton obstoječemu servisnemu računu in ga ponovno omogoči.

Stari žeton takoj ne velja več; dovoljenja ostanejo. Nov žeton se izpiše enkrat; ne
shranjujte ga v repozitorij, nastavite ga v okolje modula (M1_SERVICE_TOKEN, M2_SERVICE_TOKEN).
"""

import secrets

from django.core.management.base import BaseCommand, CommandError

from registry import models as m
from registry.services import hash_token


class Command(BaseCommand):
    help = "Zamenja žeton servisnega računa modula; stari žeton preneha veljati."

    def add_arguments(self, parser):
        parser.add_argument("name")

    def handle(self, name, **options):
        token = "svc_" + secrets.token_urlsafe(32)
        updated = m.ServiceClient.objects.filter(name=name).update(
            token_hash=hash_token(token), active=True
        )
        if not updated:
            raise CommandError("Servisni račun ne obstaja.")
        self.stdout.write(token)
