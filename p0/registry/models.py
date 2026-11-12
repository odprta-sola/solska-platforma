"""Evidenca P0: osebe, računi, oddelki, povezave in šolsko potrjena upravičenja.

Načela (glej docs/moduli/P0-uporabniki.md):
- E-naslov ni identiteta; dve osebi ali računa lahko delita naslov.
- Oseba, račun, povezava in upravičenje so ločeni pojmi. Povezava sama ne podeli pravice.
- Zgodovina se ohranja: povezave in upravičenja se zaključijo z datumom, ne brišejo.
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class ValidityQuerySet(models.QuerySet):
    def active(self, at=None):
        """Zapisi, veljavni ob času `at` (privzeto zdaj). Konec je izključen."""
        at = at or timezone.now()
        return self.filter(valid_from__lte=at).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gt=at)
        )


class Person(models.Model):
    """Stabilna evidenčna oseba. Ne pomeni nujno, da ima uporabniški račun."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=200)
    # Ni enoličen in ni identifikator: starša lahko delita naslov.
    contact_email = models.EmailField(blank=True)
    preferred_language = models.CharField(max_length=8, default="sl")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name


class Role(models.TextChoices):
    PARENT = "parent", "Starš/skrbnik"
    STUDENT = "student", "Učenec/dijak"
    TEACHER = "teacher", "Učitelj"
    OFFICE = "office", "Tajništvo/vodstvo"
    ADMIN = "admin", "Tehnični skrbnik"


class PersonRole(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="roles")
    role = models.CharField(max_length=16, choices=Role.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["person", "role"], name="uniq_person_role")]


class Account(AbstractUser):
    """Prijavni račun. Dodeljen je največ eni osebi; e-naslov ni enoličen."""

    person = models.OneToOneField(
        Person, null=True, blank=True, on_delete=models.PROTECT, related_name="account"
    )


class SourceMapping(models.Model):
    """Stabilna preslikava izvornega ključa (uvoz) v notranji ID. Omogoča ponovljiv uvoz."""

    source = models.CharField(max_length=64)
    entity_type = models.CharField(max_length=32)
    source_key = models.CharField(max_length=128)
    target_id = models.UUIDField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "entity_type", "source_key"], name="uniq_source_mapping"
            )
        ]


class Student(models.Model):
    """Učenec kot evidenčna oseba. Zapis sam ne ustvari računa."""

    person = models.OneToOneField(Person, on_delete=models.PROTECT, related_name="student")

    def __str__(self):
        return str(self.person)


class SchoolClass(models.Model):
    class_key = models.CharField(max_length=64)
    name = models.CharField(max_length=100)
    school_year = models.CharField(max_length=9)  # npr. 2026/2027

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["class_key", "school_year"], name="uniq_class_year")
        ]

    def __str__(self):
        return f"{self.name} ({self.school_year})"


class _Validity(models.Model):
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)

    objects = ValidityQuerySet.as_manager()

    class Meta:
        abstract = True


def _valid_range(name):
    return models.CheckConstraint(
        condition=Q(valid_until__isnull=True) | Q(valid_until__gt=F("valid_from")),
        name=name,
    )


class Membership(_Validity):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="memberships")
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.PROTECT, related_name="memberships"
    )

    class Meta:
        constraints = [_valid_range("membership_valid_range")]


class StaffAssignment(_Validity):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="staff_assignments")
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.PROTECT, related_name="staff_assignments"
    )

    class Meta:
        constraints = [_valid_range("staffassignment_valid_range")]


class Relationship(_Validity):
    """Preverjena povezava starš/skrbnik – učenec. Naziv sam ne podeli nobene pravice."""

    class Type(models.TextChoices):
        PARENT = "parent", "Starš"
        GUARDIAN = "guardian", "Skrbnik"

    guardian = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="relationships")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="relationships")
    relationship_type = models.CharField(max_length=16, choices=Type.choices)

    class Meta:
        constraints = [_valid_range("relationship_valid_range")]


class Approval(models.Model):
    """Šolska potrditev, ki je podlaga za upravičenje."""

    approved_by = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="approvals")
    approved_at = models.DateTimeField(default=timezone.now)
    reference = models.CharField(
        max_length=200
    )  # sklic na pooblaščeno potrditev, brez osebnih podatkov


class Grant(_Validity):
    """Upravičenje osebe za obseg in dejanje. Brez potrditve ne obstaja."""

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="grants")
    relationship = models.ForeignKey(
        Relationship, null=True, blank=True, on_delete=models.CASCADE, related_name="grants"
    )
    scope_key = models.CharField(max_length=128)
    permission = models.CharField(max_length=64)
    approval = models.ForeignKey(Approval, on_delete=models.PROTECT, related_name="grants")

    class Meta:
        constraints = [_valid_range("grant_valid_range")]


class ChangeAudit(models.Model):
    """Sled sprememb. Hrani dejanje in sklic, ne podvaja osebnih podatkov."""

    at = models.DateTimeField(default=timezone.now)
    actor = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=64)
    entity_type = models.CharField(max_length=32)
    entity_id = models.CharField(max_length=64)
    source = models.CharField(max_length=64, blank=True)
    changed_fields = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-at"]


class AccessAudit(models.Model):
    """Sled vpogledov: kdo je na zaslonih evidence odprl podatke osebe ali predogled uvoza.

    Hrani samo zaslon in sklic, nikoli prikazane vsebine, iskalnega niza, naslova IP ali
    brskalnika. Zapis nastane pred prikazom; brez zapisa ni prikaza. Rok hrambe določi D07.
    """

    at = models.DateTimeField(default=timezone.now)
    actor = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    screen = models.CharField(max_length=32)
    entity_type = models.CharField(max_length=32)
    entity_id = models.CharField(max_length=64)

    class Meta:
        ordering = ["-at"]
        indexes = [models.Index(fields=["entity_type", "entity_id", "at"])]


class ImportBatch(models.Model):
    """Ena serija uvoza CSV. Hrani povzetek in napake, ne vsebine osebnih podatkov."""

    class Status(models.TextChoices):
        PREVIEWED = "previewed", "Predogled"
        REJECTED = "rejected", "Zavrnjeno (napake ali konflikti)"
        APPLIED = "applied", "Uveljavljeno"
        FAILED = "failed", "Neuspelo"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        Person, null=True, on_delete=models.SET_NULL, related_name="import_batches"
    )
    content_hash = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status.choices)
    counts = models.JSONField(default=dict)
    problems = models.JSONField(default=list)  # napake in konflikti: datoteka, vrstica, koda
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.ForeignKey(
        Person, null=True, blank=True, on_delete=models.SET_NULL, related_name="applied_batches"
    )

    class Meta:
        ordering = ["-created_at"]


class ImportPreview(models.Model):
    """Postavka predogleda: kaj bi se zgodilo. Brez vrednosti polj, samo imena spremenjenih polj."""

    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="items")
    entity_type = models.CharField(max_length=32)
    source_key = models.CharField(max_length=256)
    action = models.CharField(max_length=16)  # create | update | unchanged
    changed_fields = models.JSONField(default=list)


class ScopeRef(models.Model):
    """Neprosojen sklic na potrjeni obseg osebe (D12). Poljuben niz ni dokaz pravice.

    Sklic izda P0 za par (oseba, scope_key) in velja samo za to osebo.
    """

    ref = models.CharField(max_length=64, unique=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="scope_refs")
    scope_key = models.CharField(max_length=128)
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["person", "scope_key"], name="uniq_scoperef_person_scope"
            )
        ]


class ServiceClient(models.Model):
    """Servisna identiteta modula (M1, M2). Žeton se hrani samo kot zgoščena vrednost."""

    name = models.CharField(max_length=64, unique=True)
    token_hash = models.CharField(max_length=64, unique=True)
    scopes = models.JSONField(default=list)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)


class ImportUpload(models.Model):
    """Začasna kopija datoteke predogleda, dokler serija ni uveljavljena ali zavržena.

    Vsebuje osebne podatke, zato se izbriše ob uveljavitvi, zavrnitvi ali po izteku
    (UPLOAD_RETENTION v registry.uploads). Ni arhiv uvozov.
    """

    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="uploads")
    name = models.CharField(max_length=32)
    content = models.BinaryField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["batch", "name"], name="uniq_upload_name")]


class AudienceSnapshot(models.Model):
    """Posnetek občinstva, ki ga je avtor potrdil v predogledu (D12, C07).

    Kontakt za dostavo se razreši samo za prejemnika iz posnetka, z aktualnim upravičenjem
    za namen posnetka in pred iztekom. P0 ne bere tabel M1/M2.
    """

    ref = models.CharField(max_length=64, unique=True)
    author = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="audiences")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT)
    purpose = models.CharField(max_length=16)
    permission = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()


class AudienceMember(models.Model):
    snapshot = models.ForeignKey(AudienceSnapshot, on_delete=models.CASCADE, related_name="members")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    scope_key = models.CharField(max_length=128)
    scope_ref = models.CharField(max_length=64)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["snapshot", "person", "scope_key"], name="uniq_audience_member"
            )
        ]
