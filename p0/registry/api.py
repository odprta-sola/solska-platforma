"""API P0 (/p0/api/v1/) po osnutku pogodbe D12 (api/openapi.yaml).

Uporabniški klic: identiteta iz preverjene seje, nikoli iz parametra.
Servisni klic: Bearer žeton modula, ločeno od seje.
"""

import json
import secrets
from functools import wraps

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_GET, require_POST

from . import authz
from . import models as m
from .services import error, issue_scope_ref, service_client, service_only


def session_person(view):
    """Zahteva prijavljen račun z osebo; sicer 401 oziroma 403 brez podrobnosti."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return error(401, "authentication_required")
        person = getattr(request.user, "person", None)
        if person is None:
            return error(403, "account_without_person")
        return view(request, person, *args, **kwargs)

    return wrapper


def json_body(request):
    try:
        body = json.loads(request.body or b"{}")
    except ValueError:
        return None
    return body if isinstance(body, dict) else None


def person_by_id(value):
    try:
        return m.Person.objects.filter(pk=value).first()
    except (ValueError, TypeError):
        return None


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
    now = timezone.now()
    items = []
    for r in rels:
        scope_key = f"student:{r.student.person_id}"
        scopes = []
        for grant in m.Grant.objects.active(now).filter(
            person=person, scope_key=scope_key, relationship=r
        ):
            ref = issue_scope_ref(person, scope_key, grant.valid_until)
            code = authz.GRANT_TO_CODE.get(grant.permission)
            if code:
                scopes.append({"scope_ref": ref.ref, "permission": code})
        items.append(
            {
                "relationship_id": r.pk,
                "student_id": str(r.student.person_id),
                "student_display_name": r.student.person.display_name,
                "relationship_type": r.relationship_type,
                "valid_from": r.valid_from.isoformat(),
                "valid_until": r.valid_until.isoformat() if r.valid_until else None,
                "scopes": scopes,
            }
        )
    return JsonResponse({"relationships": items})


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
                    "class_id": str(a.school_class_id),
                    "class_key": a.school_class.class_key,
                    "name": a.school_class.name,
                    "school_year": a.school_class.school_year,
                }
                for a in assignments
            ]
        }
    )


def _check_response(allowed, reason):
    return JsonResponse(
        {
            "allowed": allowed,
            "reason_code": reason,
            "checked_at": timezone.now().isoformat().replace("+00:00", "Z"),
        }
    )


def _check_body(request):
    body = json_body(request)
    if body is None:
        return None
    scope_ref, permission = body.get("scope_ref"), body.get("permission")
    subject_id = body.get("subject_id")
    if not isinstance(scope_ref, str) or not isinstance(permission, str):
        return None
    if subject_id is not None and not isinstance(subject_id, str):
        return None
    return scope_ref, permission, subject_id


@csrf_exempt
@require_POST
def authorization_check(request):
    """Uporabniški (seja, lastno upravičenje) ali servisni klic (Bearer, subject_id obvezen).

    Servisni klic preverja samo pravico osebe; to ni prijava v njenem imenu.
    """
    client = service_client(request)
    if client is not None:
        if "p0.authorizations.check" not in client.scopes:
            return error(403, "service_scope_missing")
        parsed = _check_body(request)
        if parsed is None or parsed[2] is None:
            return error(400, "invalid_request")
        scope_ref, permission, subject_id = parsed
        subject = person_by_id(subject_id)
        if subject is None:
            return _check_response(False, "NOT_ALLOWED")
        return _check_response(*authz.check_scope(subject, scope_ref, permission))
    if request.headers.get("Authorization", "").startswith("Bearer "):
        return error(401, "invalid_service_identity")  # neveljaven žeton ne preide na sejo
    return csrf_protect(_session_check)(request)


@session_person
def _session_check(request, person):
    parsed = _check_body(request)
    if parsed is None:
        return error(400, "invalid_request")
    scope_ref, permission, subject_id = parsed
    if subject_id is not None and subject_id != str(person.pk):
        return error(403, "subject_not_self")
    return _check_response(*authz.check_scope(person, scope_ref, permission))


PURPOSE_PERMISSION = {"notice": "acknowledge", "form": "decide"}


@require_POST
@service_only("p0.audiences.resolve")
def audiences_resolve(request, client):
    """Predogled dovoljenih prejemnikov oddelka za pooblaščenega avtorja.

    Avtor mora imeti veljavno dodelitev oddelka. Vrne scope_ref in prikazno oznako,
    nikoli kontaktov. Delegiranje avtorja po seji ostaja odprto v D12.
    """
    body = json_body(request)
    if body is None:
        return error(400, "invalid_request")
    author = person_by_id(body.get("author_id")) if isinstance(body.get("author_id"), str) else None
    purpose = body.get("purpose")
    class_id = body.get("class_id")
    if purpose not in PURPOSE_PERMISSION or not isinstance(class_id, str) or author is None:
        return error(400, "invalid_request")
    now = timezone.now()
    if not (
        class_id.isdigit()
        and m.StaffAssignment.objects.active(now)
        .filter(person=author, school_class_id=int(class_id))
        .exists()
    ):
        return error(403, "author_not_assigned")
    permission = PURPOSE_PERMISSION[purpose]
    students = m.Student.objects.filter(
        memberships__in=m.Membership.objects.active(now).filter(school_class_id=int(class_id))
    ).distinct()
    recipients = []
    for student in students.order_by("person__display_name"):
        scope_key = f"student:{student.person_id}"
        rels = (
            m.Relationship.objects.active(now)
            .filter(student=student)
            .select_related("guardian")
            .order_by("guardian__display_name")
        )
        for rel in rels:
            allowed, _ = authz.check_grant(rel.guardian, scope_key, permission, now)
            if not allowed:
                continue
            grant = (
                m.Grant.objects.active(now)
                .filter(person=rel.guardian, scope_key=scope_key, permission=permission)
                .first()
            )
            ref = issue_scope_ref(rel.guardian, scope_key, grant.valid_until if grant else None)
            recipients.append(
                {
                    "person_id": str(rel.guardian_id),
                    "scope_ref": ref.ref,
                    "display_label": rel.guardian.display_name,
                    "student_label": student.person.display_name,
                }
            )
    return JsonResponse(
        {
            "audience_ref": "au_" + secrets.token_urlsafe(12),
            "version": 1,
            "previewed_at": now.isoformat().replace("+00:00", "Z"),
            "recipients": recipients,
        }
    )


@require_POST
@service_only("p0.contacts.resolve")
def delivery_contact_resolve(request, client):
    """Kontakt za točno določenega prejemnika tik pred pošiljanjem; samo M1.

    Veljati mora aktualno upravičenje za obseg. Kontakta ni mogoče brati z ugibanimi ID.
    """
    body = json_body(request)
    if body is None:
        return error(400, "invalid_request")
    recipient_id, scope_ref = body.get("recipient_id"), body.get("scope_ref")
    request_id = body.get("delivery_request_id")
    if not all(isinstance(v, str) and v for v in (recipient_id, scope_ref, request_id)):
        return error(400, "invalid_request")
    person = person_by_id(recipient_id)
    ref = m.ScopeRef.objects.filter(ref=scope_ref, person=person).first() if person else None
    if person is None or ref is None:
        return error(403, "scope_not_allowed")
    now = timezone.now()
    if ref.expires_at is not None and ref.expires_at <= now:
        return error(403, "scope_not_allowed")
    entitled = any(
        authz.check_grant(person, ref.scope_key, perm, now)[0] for perm in authz.GRANT_TO_CODE
    )
    if not entitled:
        return error(403, "scope_not_allowed")
    if not person.contact_email:
        return JsonResponse({"deliverable": False, "reason_code": "NO_CONTACT"})
    return JsonResponse(
        {
            "deliverable": True,
            "reason_code": "OK",
            "email": person.contact_email,
            "locale": person.preferred_language,
        }
    )
