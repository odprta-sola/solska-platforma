"""API P0 (/p0/api/v1/) po osnutku pogodbe D12 (api/openapi.yaml).

Uporabniški klic: identiteta iz preverjene seje, nikoli iz parametra.
Servisni klic: Bearer žeton modula, ločeno od seje.
"""

import json
import re
import secrets
from datetime import timedelta
from functools import wraps

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_GET, require_POST

from . import authz
from . import models as m
from .contract_schemas import valid_request
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
    """Oseba po ID ali None; neveljavna oblika ID je enaka neobstoječi osebi."""
    try:
        return m.Person.objects.filter(pk=value).first()
    except (ValueError, TypeError, ValidationError):
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
    if not valid_request("AuthCheckRequest", body):
        return None
    return body["scope_ref"], body["permission"], body.get("subject_id")


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


CLASS_ID = re.compile(r"[0-9]{1,18}")  # ASCII števke v obsegu bigint
PURPOSE_PERMISSION = {"notice": "acknowledge", "form": "decide"}


AUDIENCE_TTL = timedelta(days=30)  # predlog D12: rok uporabe posnetka; nato izbris (audiences)


@require_POST
@session_person
def audiences_resolve(request, person):
    """Predogled dovoljenih prejemnikov oddelka za prijavljenega avtorja (seja in CSRF).

    Avtor je oseba iz seje in mora imeti veljavno dodelitev oddelka. P0 shrani posnetek
    občinstva (`audience_ref`), na katerega se veže razrešitev kontaktov ob dostavi.
    Odgovor vsebuje sklice in prikazne oznake, nikoli kontaktov.
    """
    body = json_body(request)
    if not valid_request("AudienceRequest", body):
        return error(400, "invalid_request")
    purpose, class_id = body["purpose"], body["class_id"]
    now = timezone.now()
    assignment = (
        m.StaffAssignment.objects.active(now)
        .filter(person=person, school_class_id=int(class_id))
        .first()
        if CLASS_ID.fullmatch(class_id)
        else None
    )
    if assignment is None:
        return error(403, "author_not_assigned")
    permission = PURPOSE_PERMISSION[purpose]
    students = m.Student.objects.filter(
        memberships__in=m.Membership.objects.active(now).filter(school_class_id=int(class_id))
    ).distinct()
    snapshot = m.AudienceSnapshot.objects.create(
        ref="au_" + secrets.token_urlsafe(16),
        author=person,
        school_class_id=int(class_id),
        purpose=purpose,
        permission=permission,
        created_at=now,
        expires_at=now + AUDIENCE_TTL,
    )
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
            m.AudienceMember.objects.get_or_create(
                snapshot=snapshot,
                person=rel.guardian,
                scope_key=scope_key,
                defaults={"scope_ref": ref.ref},
            )
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
            "audience_ref": snapshot.ref,
            "version": 1,
            "previewed_at": now.isoformat().replace("+00:00", "Z"),
            "expires_at": snapshot.expires_at.isoformat().replace("+00:00", "Z"),
            "recipients": recipients,
        }
    )


@require_POST
@service_only("p0.contacts.resolve")
def delivery_contact_resolve(request, client):
    """Kontakt za prejemnika dostave tik pred pošiljanjem; samo M1 (D12, C07).

    Kontakt se vrne samo, če je prejemnik s tem sklicem v posnetku občinstva (`audience_ref`),
    posnetek ni potekel in ima prejemnik aktualno upravičenje za namen posnetka. Vsak drug
    vhod (tuj, neobstoječ, potekel, odvzet) dobi enak odgovor 403.
    """
    body = json_body(request)
    if not valid_request("ContactRequest", body):
        return error(400, "invalid_request")
    member = delivery_binding(body["audience_ref"], body["recipient_id"], body["scope_ref"])
    if member is None:
        return error(403, "scope_not_allowed")
    return _resolve_contact(member)


def delivery_binding(audience_ref, recipient_id, scope_ref, at=None):
    """Član veljavnega posnetka občinstva za prejemnika in sklic ali None."""
    at = at or timezone.now()
    person = person_by_id(recipient_id)
    if person is None:
        return None
    return (
        m.AudienceMember.objects.select_related("snapshot", "person")
        .filter(
            snapshot__ref=audience_ref,
            snapshot__expires_at__gt=at,
            person=person,
            scope_ref=scope_ref,
        )
        .first()
    )


def _resolve_contact(member):
    """Kontakt za člana posnetka, če ima aktualno upravičenje za namen posnetka."""
    person, snapshot = member.person, member.snapshot
    now = timezone.now()
    ref = m.ScopeRef.objects.filter(ref=member.scope_ref, person=person).first()
    if ref is None or (ref.expires_at is not None and ref.expires_at <= now):
        return error(403, "scope_not_allowed")
    if not authz.check_grant(person, member.scope_key, snapshot.permission, now)[0]:
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
