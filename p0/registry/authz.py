"""Preverjanje upravičenj. Edino mesto, kjer se odloča, ali je dejanje dovoljeno.

Pravila (docs/arhitektura/kratka-specifikacija-P0-M1-M2.md, 5 in 3):
- Povezava sama ne dovoli dejanja; potrebno je šolsko potrjeno upravičenje (Grant).
- Odvzem povezave prevlada nad sicer veljavnim upravičenjem vezanim nanjo.
- Odvzem upravičenja prevlada nad veljavno povezavo.
- Napaka ali neznan obseg nikoli ne pomeni »dovoljeno«.
"""

from django.db import transaction
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


@transaction.atomic
def revoke_relationship(relationship, actor=None, source="", at=None):
    at = at or timezone.now()
    relationship.valid_until = at
    relationship.save(update_fields=["valid_until"])
    m.ChangeAudit.objects.create(
        at=at,
        actor=actor,
        action="relationship.revoked",
        entity_type="relationship",
        entity_id=str(relationship.pk),
        source=source,
        changed_fields=["valid_until"],
    )


@transaction.atomic
def revoke_grant(grant, actor=None, source="", at=None):
    at = at or timezone.now()
    grant.valid_until = at
    grant.save(update_fields=["valid_until"])
    m.ChangeAudit.objects.create(
        at=at,
        actor=actor,
        action="grant.revoked",
        entity_type="grant",
        entity_id=str(grant.pk),
        source=source,
        changed_fields=["valid_until"],
    )


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
