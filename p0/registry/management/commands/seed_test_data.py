"""Naloži izmišljeni testni nabor (docs/moduli/P0-uporabniki.md). Ponovljiv in idempotenten.

Gesla se ne shranijo v kodo: računi imajo neuporabno geslo, razen če je v okolju
SEED_PASSWORD (samo za lokalni razvoj).
"""

import os

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from registry import models as m

SOURCE = "testni-nabor"
SCHOOL_YEAR = "2026/2027"

PEOPLE = [
    # key, name, email, role
    ("staff-01", "Učitelj Testni 01", "staff01@example.invalid", m.Role.TEACHER),
    ("staff-02", "Učitelj Testni 02", "staff02@example.invalid", m.Role.TEACHER),
    ("staff-03", "Tajništvo Testno 03", "staff03@example.invalid", m.Role.OFFICE),
    ("parent-01", "Starš Testni 01", "family01@example.invalid", m.Role.PARENT),
    ("parent-02", "Starš Testni 02", "family01@example.invalid", m.Role.PARENT),  # skupni kontakt
    ("parent-03", "Starš Testni 03", "family03@example.invalid", m.Role.PARENT),
    ("parent-04", "Starš Testni 04", "", m.Role.PARENT),  # brez e-pošte, papirna pot
    ("student-01", "Učenec Testni 01", "", m.Role.STUDENT),
    ("student-02", "Učenec Testni 02", "", m.Role.STUDENT),
    ("student-03", "Učenec Testni 03", "", m.Role.STUDENT),
    ("student-04", "Učenec Testni 04", "", m.Role.STUDENT),
]
CLASSES = {"razred-7a": "7. a", "razred-8b": "8. b"}
MEMBERSHIPS = {
    "student-01": "razred-7a",
    "student-02": "razred-8b",
    "student-03": "razred-7a",
    "student-04": "razred-7a",
}
ASSIGNMENTS = {"staff-01": "razred-7a", "staff-02": "razred-8b"}
RELATIONSHIPS = [
    ("parent-01", "student-01"),
    ("parent-01", "student-02"),
    ("parent-02", "student-01"),
    ("parent-03", "student-03"),
    ("parent-04", "student-04"),
]
# Računi: starši, učitelji in tajništvo; učenci nimajo računa (predlog je v pregledu).
ACCOUNTS = [k for k, _, _, role in PEOPLE if role != m.Role.STUDENT]


class Command(BaseCommand):
    help = "Naloži izmišljeni testni nabor (idempotentno)."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()
        start = now.replace(month=9, day=1, hour=0, minute=0, second=0, microsecond=0)
        if start > now:
            start = start.replace(year=start.year - 1)
        password = os.environ.get("SEED_PASSWORD")

        persons = {}
        for key, name, email, role in PEOPLE:
            mp = m.SourceMapping.objects.filter(
                source=SOURCE, entity_type="person", source_key=key
            ).first()
            if mp:
                person = m.Person.objects.get(pk=mp.target_id)
            else:
                person = m.Person.objects.create(display_name=name, contact_email=email)
                m.SourceMapping.objects.create(
                    source=SOURCE, entity_type="person", source_key=key, target_id=person.pk
                )
            m.PersonRole.objects.get_or_create(person=person, role=role)
            persons[key] = person

        students = {}
        for key, person in persons.items():
            if key.startswith("student-"):
                students[key], _ = m.Student.objects.get_or_create(person=person)

        classes = {}
        for key, name in CLASSES.items():
            classes[key], _ = m.SchoolClass.objects.get_or_create(
                class_key=key, school_year=SCHOOL_YEAR, defaults={"name": name}
            )

        for skey, ckey in MEMBERSHIPS.items():
            m.Membership.objects.get_or_create(
                student=students[skey], school_class=classes[ckey], defaults={"valid_from": start}
            )
        for pkey, ckey in ASSIGNMENTS.items():
            m.StaffAssignment.objects.get_or_create(
                person=persons[pkey], school_class=classes[ckey], defaults={"valid_from": start}
            )

        approval, _ = m.Approval.objects.get_or_create(
            approved_by=persons["staff-03"], reference="testni-nabor-potrditev"
        )
        for gkey, skey in RELATIONSHIPS:
            rel, _ = m.Relationship.objects.get_or_create(
                guardian=persons[gkey],
                student=students[skey],
                defaults={"relationship_type": m.Relationship.Type.PARENT, "valid_from": start},
            )
            m.Grant.objects.get_or_create(
                person=persons[gkey],
                relationship=rel,
                scope_key=f"student:{persons[skey].pk}",
                permission="acknowledge",
                defaults={"valid_from": start, "approval": approval},
            )

        for key in ACCOUNTS:
            account, created = m.Account.objects.get_or_create(
                username=key, defaults={"person": persons[key]}
            )
            if created:
                account.email = persons[key].contact_email
                if password:
                    account.set_password(password)
                else:
                    account.set_unusable_password()
                account.save()
            elif password:
                # Ponovni zagon s SEED_PASSWORD nastavi geslo tudi obstoječim testnim računom.
                account.set_password(password)
                account.save(update_fields=["password"])

        self.stdout.write(self.style.SUCCESS("Testni nabor naložen."))
