"""Uporabniški API P0 (/p0/api/v1/). Identiteta je vedno iz preverjene seje, nikoli iz parametra."""

import json
from functools import wraps

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from . import authz
from . import models as m


def _error(status, code):
    return JsonResponse({"error": code}, status=status)


def session_person(view):
    """Zahteva prijavljen račun z osebo; sicer 401 oziroma 403 brez podrobnosti."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _error(401, "authentication_required")
        person = getattr(request.user, "person", None)
        if person is None:
            return _error(403, "account_without_person")
        return view(request, person, *args, **kwargs)

    return wrapper


@require_GET
@session_person
def me(request, person):
    return JsonResponse(
        {
            "person_id": str(person.pk),
            "display_name": person.display_name,
            "roles": sorted(person.roles.values_list("role", flat=True)),
            "preferred_language": person.preferred_language,
        }
    )


@require_GET
@session_person
def my_relationships(request, person):
    rels = (
        m.Relationship.objects.active()
        .filter(guardian=person)
        .select_related("student__person")
        .order_by("student__person__display_name")
    )
    return JsonResponse(
        {
            "relationships": [
                {
                    "relationship_id": r.pk,
                    "student_id": str(r.student.person_id),
                    "student_display_name": r.student.person.display_name,
                    "relationship_type": r.relationship_type,
                    "valid_from": r.valid_from.isoformat(),
                    "valid_until": r.valid_until.isoformat() if r.valid_until else None,
                }
                for r in rels
            ]
        }
    )


@require_GET
@session_person
def my_classes(request, person):
    assignments = (
        m.StaffAssignment.objects.active()
        .filter(person=person)
        .select_related("school_class")
        .order_by("school_class__class_key")
    )
    return JsonResponse(
        {
            "classes": [
                {
                    "class_key": a.school_class.class_key,
                    "name": a.school_class.name,
                    "school_year": a.school_class.school_year,
                }
                for a in assignments
            ]
        }
    )


@require_POST
@session_person
def authorization_check(request, person):
    """Ali ima prijavljena oseba aktualno upravičenje za obseg in dejanje.

    Preverja samo lastno upravičenje. Preverjanje za drugo osebo (servisni klic) še ni
    na voljo in zahteva servisno identiteto iz D12.
    """
    try:
        body = json.loads(request.body or b"{}")
        scope_key = body["scope_key"]
        permission = body["permission"]
    except (ValueError, KeyError):
        return _error(400, "invalid_request")
    if not (isinstance(scope_key, str) and isinstance(permission, str)):
        return _error(400, "invalid_request")
    allowed, reason = authz.check_grant(person, scope_key, permission)
    return JsonResponse({"allowed": allowed, "reason": reason})
