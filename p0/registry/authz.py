"""Preverjanje upravičenj. Edino mesto, kjer se odloča, ali je dejanje dovoljeno.

Pravila (docs/arhitektura/kratka-specifikacija-P0-M1-M2.md, 5 in 3):
- Povezava sama ne dovoli dejanja; potrebno je šolsko potrjeno upravičenje (Grant).
- Odvzem povezave prevlada nad sicer veljavnim upravičenjem vezanim nanjo.
- Odvzem upravičenja prevlada nad veljavno povezavo.
- Napaka ali neznan obseg nikoli ne pomeni »dovoljeno«.
"""

import hashlib
from datetime import timedelta

from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone

from . import models as m

# Šifrant dovoljenj modulov (D12): koda v pogodbi -> dovoljenje v upravičenju.
PERMISSION_CODES = {"m1.confirm": "acknowledge", "m2.decide": "decide"}
GRANT_TO_CODE = {v: k for k, v in PERMISSION_CODES.items()}

OK = "ok"
NO_GRANT = "no_grant"
RELATIONSHIP_INACTIVE = "relationship_inactive"


def check_grant(person, scope_key, permission, at=None):
    """Vrne (dovoljeno, koda razloga). Koda ne razkriva, ali obseg obstaja pri drugi osebi."""
    at = at or timezone.now()
    grants = (
        m.Grant.objects.active(at)
        .filter(person=person, scope_key=scope_key, permission=permission)
        .select_related("relationship")
    )
    saw_inactive_relationship = False
    for grant in grants:
        rel = grant.relationship
        if rel is None:
            return True, OK
        if m.Relationship.objects.active(at).filter(pk=rel.pk).exists():
            return True, OK
        saw_inactive_relationship = True
    return False, RELATIONSHIP_INACTIVE if saw_inactive_relationship else NO_GRANT


def _advisory_lock(*parts):
    """Transakcijska ključavnica PostgreSQL za poslovni obseg (sprosti se ob koncu transakcije)."""
    digest = hashlib.sha256(":".join(str(p) for p in parts).encode()).digest()
    key = int.from_bytes(digest[:8], "big", signed=True)
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", [key])


def lock_relationship_scope(guardian_id, student_id):
    """Uskladi uvoz in odvzem povezav istega skrbnika in učenca."""
    _advisory_lock("relationship", guardian_id, student_id)


def lock_grant_scope(person_id, scope_key, permission):
    """Uskladi uvoz in odvzem upravičenj iste osebe, obsega in dovoljenja."""
    _advisory_lock("grant", person_id, scope_key, permission)


def _end_all(queryset, entity_type, actor, source, at):
    """Zaključi vse še veljavne ali prihodnje zapise obsega in za vsakega zapiše sled."""
    for obj in queryset.select_for_update().filter(
        Q(valid_until__isnull=True) | Q(valid_until__gt=at)
    ):
        # Ograda zahteva valid_until > valid_from; prihodnji zapis se zaključi takoj ob začetku.
        obj.valid_until = max(at, obj.valid_from + timedelta(microseconds=1))
        obj.save(update_fields=["valid_until"])
        m.ChangeAudit.objects.create(
            at=at,
            actor=actor,
            action=f"{entity_type}.revoked",
            entity_type=entity_type,
            entity_id=str(obj.pk),
            source=source,
            changed_fields=["valid_until"],
        )


@transaction.atomic
def revoke_relationship(relationship, actor=None, source="", at=None):
    """Odvzem velja za poslovni obseg (skrbnik, učenec), ne le za izbrano vrstico."""
    lock_relationship_scope(relationship.guardian_id, relationship.student_id)
    at = at or timezone.now()
    scope = m.Relationship.objects.filter(
        guardian_id=relationship.guardian_id, student_id=relationship.student_id
    )
    _end_all(scope, "relationship", actor, source, at)
    relationship.refresh_from_db(fields=["valid_until"])


@transaction.atomic
def revoke_grant(grant, actor=None, source="", at=None):
    """Odvzem velja za poslovni obseg (oseba, obseg, dovoljenje), ne le za izbrano vrstico."""
    lock_grant_scope(grant.person_id, grant.scope_key, grant.permission)
    at = at or timezone.now()
    scope = m.Grant.objects.filter(
        person_id=grant.person_id, scope_key=grant.scope_key, permission=grant.permission
    )
    _end_all(scope, "grant", actor, source, at)
    grant.refresh_from_db(fields=["valid_until"])


def check_scope(subject, scope_ref, permission_code, at=None):
    """Preverjanje po pogodbi D12. Vrne (dovoljeno, reason_code).

    Neznan ali tuj sklic je NOT_ALLOWED, da ne razkrije obstoja tujih obsegov.
    Razlogi so ALLOWED, NOT_ALLOWED, SCOPE_INACTIVE.
    """
    at = at or timezone.now()
    permission = PERMISSION_CODES.get(permission_code)
    ref = m.ScopeRef.objects.filter(ref=scope_ref, person=subject).first()
    if permission is None or ref is None:
        return False, "NOT_ALLOWED"
    if ref.expires_at is not None and ref.expires_at <= at:
        return False, "SCOPE_INACTIVE"
    allowed, _ = check_grant(subject, ref.scope_key, permission, at)
    return (True, "ALLOWED") if allowed else (False, "NOT_ALLOWED")
