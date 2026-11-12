"""Uvoz CSV: najprej predogled, nato uveljavitev izrecne serije.

python manage.py import_csv MAPA --source viri --actor uporabnik
python manage.py import_csv MAPA --source viri --actor uporabnik --apply-batch <ID>
"""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from registry import importer
from registry import models as m


class Command(BaseCommand):
    help = "Uvozi CSV v evidenco P0 (predogled ali uveljavitev pregledane serije)."

    def add_arguments(self, parser):
        parser.add_argument("directory")
        parser.add_argument("--source", required=True)
        parser.add_argument("--actor", required=True, help="Uporabniško ime pooblaščene osebe")
        parser.add_argument("--apply-batch", help="ID pregledane serije, ki jo uveljavimo")

    def handle(self, directory, source, actor, apply_batch=None, **options):
        account = m.Account.objects.filter(username=actor).select_related("person").first()
        if account is None or account.person is None:
            raise CommandError("Neznan ali neveljaven pooblaščeni račun.")
        folder = Path(directory)
        files = {p.stem: p.read_bytes() for p in sorted(folder.glob("*.csv"))}

        if apply_batch:
            batch = m.ImportBatch.objects.filter(pk=apply_batch, source=source).first()
            if batch is None:
                raise CommandError("Serija ne obstaja.")
            try:
                batch, result = importer.apply_batch(batch, files, account.person)
            except ValueError as exc:
                raise CommandError(str(exc)) from exc
            if batch.status != m.ImportBatch.Status.APPLIED:
                self._report(result)
                raise CommandError("Uvoz ni bil uveljavljen; spremembe niso zapisane.")
            self.stdout.write(self.style.SUCCESS(f"Uveljavljeno: {batch.id}"))
            self._counts(result)
            return

        batch, result = importer.preview(files, source, account.person)
        self._counts(result)
        if not result.clean:
            self._report(result)
            raise CommandError(f"Predogled zavrnjen (serija {batch.id}). Nič ni bilo spremenjeno.")
        self.stdout.write(self.style.SUCCESS(f"Predogled v redu. Serija: {batch.id}"))
        self.stdout.write(f"Uveljavitev: --apply-batch {batch.id}")

    def _counts(self, result):
        for entity, c in sorted(result.counts.items()):
            self.stdout.write(f"  {entity}: +{c['create']} ~{c['update']} ={c['unchanged']}")

    def _report(self, result):
        for p in result.problems:
            self.stderr.write(f"  [{p.kind}] {p.file}:{p.row} {p.code} {p.message}")
