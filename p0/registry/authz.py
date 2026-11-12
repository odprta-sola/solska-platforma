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
