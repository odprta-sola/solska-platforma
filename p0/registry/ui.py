"""Zasloni evidence za tajništvo in skrbnika (obseg T: uvoz, osebe z odvzemom, kontakt).

Odločanje o pravicah ostane v authz.py in importer.py; zasloni so le vmesnik do njih.
Vsak zaslon zahteva prijavo in vlogo office ali admin; CSRF velja za vse obrazce.
"""

from functools import wraps
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from . import authz, export, importer, uploads
from . import models as m
from .forms import ContactForm, ImportForm, SearchForm

STAFF_ROLES = {m.Role.OFFICE.value, m.Role.ADMIN.value}
ITEMS_PER_PAGE = 200  # predogled: vse postavke so dosegljive po straneh
PERMISSION_LABELS = {"acknowledge": "seznanitev (M1)", "decide": "odločanje (M2)"}
SCREEN_SOURCE = "zaslon"  # vir v sledi; ni "import:", zato šteje kot ročna sprememba


def record_view(actor, screen, entity_type, entity_id):
    """Zapiše vpogled v sled (AccessAudit) pred prikazom podatkov."""
    m.AccessAudit.objects.create(
        actor=actor, screen=screen, entity_type=entity_type, entity_id=str(entity_id)
    )


def is_staff(user):
    person = getattr(user, "person", None) if user.is_authenticated else None
    return bool(person) and person.roles.filter(role__in=STAFF_ROLES).exists()


def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not is_staff(request.user):
            return render(request, "evidenca/403.html", status=403)
        return view(request, request.user.person, *args, **kwargs)

    return wrapper


@require_http_methods(["GET"])
def home(request):
    """Začetna stran po prijavi."""
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    return render(request, "evidenca/zacetek.html", {"staff": is_staff(request.user)})


# Osebe ---------------------------------------------------------------------------------


@require_http_methods(["GET"])
@staff_required
def persons(request, actor):
    form = SearchForm(request.GET or None)
    qs = m.Person.objects.prefetch_related("roles").order_by("display_name")
    q = form.cleaned_data["q"] if form.is_valid() else ""
    if q:
        qs = qs.filter(display_name__icontains=q)
    page = Paginator(qs, 50).get_page(request.GET.get("stran"))
    return render(request, "evidenca/osebe.html", {"form": form, "page": page, "q": q})


def _student_names(scope_keys):
    ids = [k.split(":", 1)[1] for k in scope_keys if k.startswith("student:")]
    return dict((f"student:{p.pk}", p.display_name) for p in m.Person.objects.filter(pk__in=ids))


def _open(obj, now):
    """Zapis še ni zaključen: velja zdaj ali začne veljati pozneje (odvzem je še smiseln)."""
    return obj.valid_until is None or obj.valid_until > now


def _rel_state(rel, active, now):
    if rel.valid_from > now:
        return "še ne velja"
    return "veljavna" if active else "zaključena"


def _grant_state(grant, active, active_relationships, now=None):
    """Stanje, kot ga vidi authz: upravičenje na zaključeni povezavi ne velja."""
    if now and grant.valid_from > now:
        return "še ne velja"
    if not active:
        return "zaključeno"
    if grant.relationship_id and grant.relationship_id not in active_relationships:
        return "ne velja: povezava je zaključena"
    return "veljavno"


@require_http_methods(["GET"])
@staff_required
def person_detail(request, actor, person_id):
    person = get_object_or_404(m.Person, pk=person_id)
    record_view(actor, "oseba", "person", person.pk)
    now = timezone.now()
    active_rel = set(m.Relationship.objects.active(now).values_list("pk", flat=True))
    active_grant = set(
        m.Grant.objects.active(now).filter(person=person).values_list("pk", flat=True)
    )
    as_guardian = person.relationships.select_related("student__person").order_by("-valid_from")
    as_student = m.Relationship.objects.filter(student__person=person).select_related("guardian")
    grants = list(
        m.Grant.objects.filter(person=person).select_related("relationship").order_by("-valid_from")
    )
    names = _student_names({g.scope_key for g in grants})
    entity_ids = (
        [str(person.pk)]
        + [str(r.pk) for r in as_guardian]
        + [str(r.pk) for r in as_student]
        + [str(g.pk) for g in grants]
    )
    audit = m.ChangeAudit.objects.filter(entity_id__in=entity_ids).select_related("actor")[:20]
    return render(
        request,
        "evidenca/oseba.html",
        {
            "person": person,
            "roles": person.roles.all(),
            "as_guardian": [
                (r, _open(r, now), _rel_state(r, r.pk in active_rel, now)) for r in as_guardian
            ],
            "as_student": [(r, _rel_state(r, r.pk in active_rel, now)) for r in as_student],
            "grants": [
                (
                    g,
                    _open(g, now),
                    _grant_state(g, g.pk in active_grant, active_rel, now),
                    names.get(g.scope_key, "—"),
                    PERMISSION_LABELS.get(g.permission, g.permission),
                )
                for g in grants
            ],
            "audit": audit,
        },
    )


@require_POST
@staff_required
def person_export(request, actor, person_id):
    """Prenos vseh podatkov osebe v JSON (zahteva po dostopu). Zapis v sled pred izvozom."""
    person = get_object_or_404(m.Person, pk=person_id)
    record_view(actor, "izvoz", "person", person.pk)
    now = timezone.now()
    response = JsonResponse(
        export.person_export(person, now),
        json_dumps_params={"ensure_ascii": False, "indent": 2},
    )
    name = f"izvoz-osebe-{person.pk}-{now:%Y%m%d}.json"
    response["Content-Disposition"] = f'attachment; filename="{name}"'
    response["Cache-Control"] = "no-store"
    return response


def _not_ended(manager):
    now = timezone.now()
    return manager.filter(Q(valid_until__isnull=True) | Q(valid_until__gt=now))


def _revoke(request, actor, person, obj, kind, label, revoke):
    record_view(actor, f"odvzem:{obj._meta.model_name}", "person", person.pk)
    if request.method == "POST":
        revoke(obj, actor=actor, source=SCREEN_SOURCE)
        messages.success(request, f"Odvzem je izveden: {label}. Sprememba je zabeležena v sledi.")
        return redirect("ui-person", person_id=person.pk)
    return render(
        request,
        "evidenca/odvzem.html",
        {"person": person, "kind": kind, "label": label, "obj": obj},
    )


@require_http_methods(["GET", "POST"])
@staff_required
def revoke_relationship(request, actor, person_id, rel_id):
    person = get_object_or_404(m.Person, pk=person_id)
    rel = get_object_or_404(
        _not_ended(m.Relationship.objects).select_related("guardian", "student__person"),
        pk=rel_id,
        guardian=person,
    )
    label = f"Povezava {rel.guardian.display_name} – {rel.student.person.display_name}"
    return _revoke(request, actor, person, rel, "povezava", label, authz.revoke_relationship)


@require_http_methods(["GET", "POST"])
@staff_required
def revoke_grant(request, actor, person_id, grant_id):
    person = get_object_or_404(m.Person, pk=person_id)
    grant = get_object_or_404(_not_ended(m.Grant.objects), pk=grant_id, person=person)
    student = _student_names([grant.scope_key]).get(grant.scope_key, "—")
    perm = PERMISSION_LABELS.get(grant.permission, grant.permission)
    label = f"Upravičenje »{perm}« za {student}"
    return _revoke(request, actor, person, grant, "upravičenje", label, authz.revoke_grant)


@require_http_methods(["GET", "POST"])
@staff_required
def contact(request, actor, person_id):
    person = get_object_or_404(m.Person, pk=person_id)
    record_view(actor, "kontakt", "person", person.pk)
    form = ContactForm(request.POST or None, instance=person)
    if request.method == "POST" and form.is_valid():
        if form.has_changed():
            with transaction.atomic():
                form.save()
                m.ChangeAudit.objects.create(
                    actor=actor,
                    action="person.contact_updated",
                    entity_type="person",
                    entity_id=str(person.pk),
                    source=SCREEN_SOURCE,
                    changed_fields=form.changed_data,
                )
            messages.success(request, "Kontakt je posodobljen. Sprememba je zabeležena v sledi.")
        else:
            messages.success(request, "Kontakt je nespremenjen.")
        return redirect("ui-person", person_id=person.pk)
    return render(request, "evidenca/kontakt.html", {"person": person, "form": form})


# Uvoz ----------------------------------------------------------------------------------


def _purge_stale_uploads():
    uploads.purge_expired()


def _expire(batch):
    """Če je predogled potekel, takoj izbriše njegove datoteke. Vrne True ob izteku."""
    if uploads.expired(batch):
        m.ImportUpload.objects.filter(batch=batch).delete()
        return True
    return False


def _read_uploads(uploaded, form):
    files = {}
    for f in uploaded:
        name = Path(f.name).stem
        if name in files:
            form.add_error("files", f"Datoteka {name} je izbrana dvakrat.")
            return None
        if f.size > importer.MAX_FILE_BYTES:
            form.add_error("files", f"Datoteka {f.name} je prevelika.")
            return None
        files[name] = f.read()
    return files


@require_http_methods(["GET", "POST"])
@staff_required
def import_index(request, actor):
    _purge_stale_uploads()
    form = ImportForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        files = _read_uploads(form.cleaned_data["files"], form)
        if files is not None:
            batch, _ = importer.preview(files, form.cleaned_data["source"], actor)
            if batch.status == m.ImportBatch.Status.PREVIEWED:
                m.ImportUpload.objects.bulk_create(
                    m.ImportUpload(batch=batch, name=k, content=v) for k, v in files.items()
                )
            return redirect("ui-import-batch", batch_id=batch.pk)
    batches = m.ImportBatch.objects.select_related("created_by")[:20]
    return render(request, "evidenca/uvoz.html", {"form": form, "batches": batches})


@require_http_methods(["GET"])
@staff_required
def import_batch(request, actor, batch_id):
    batch = get_object_or_404(m.ImportBatch, pk=batch_id)
    record_view(actor, "uvoz", "import_batch", batch.pk)
    _expire(batch)
    items = batch.items.order_by("pk")
    only_changes = request.GET.get("samo") == "spremembe"
    shown = items.exclude(action="unchanged") if only_changes else items
    page = Paginator(shown, ITEMS_PER_PAGE).get_page(request.GET.get("stran"))
    return render(
        request,
        "evidenca/serija.html",
        {
            "batch": batch,
            "page": page,
            "only_changes": only_changes,
            "item_count": items.count(),
            "changes": items.exclude(action="unchanged").count(),
            "can_apply": batch.status == m.ImportBatch.Status.PREVIEWED and batch.uploads.exists(),
        },
    )


@require_POST
@staff_required
def import_apply(request, actor, batch_id):
    batch = get_object_or_404(m.ImportBatch, pk=batch_id)
    not_after = uploads.deadline(batch)
    if _expire(batch):
        messages.error(request, "Predogled je potekel (starejši od 24 ur). Naredite nov predogled.")
        return redirect("ui-import-batch", batch_id=batch.pk)
    files = {u.name: bytes(u.content) for u in batch.uploads.all()}
    if not files:
        messages.error(request, "Datoteke predogleda niso več na voljo. Naredite nov predogled.")
        return redirect("ui-import-batch", batch_id=batch.pk)
    try:
        batch, result = importer.apply_batch(batch, files, actor, not_after=not_after)
    except ValueError as exc:
        if uploads.expired(batch):
            m.ImportUpload.objects.filter(batch=batch).delete()
        messages.error(request, f"Serije ni bilo mogoče uveljaviti: {exc}")
        return redirect("ui-import-batch", batch_id=batch.pk)
    m.ImportUpload.objects.filter(batch=batch).delete()
    if result.clean:
        messages.success(request, "Serija je uveljavljena.")
    else:
        messages.error(request, "Serija ni uveljavljena. Razlogi so navedeni spodaj.")
    return redirect("ui-import-batch", batch_id=batch.pk)


@require_POST
@staff_required
def import_discard(request, actor, batch_id):
    with transaction.atomic():
        batch = get_object_or_404(m.ImportBatch.objects.select_for_update(), pk=batch_id)
        previewed = batch.status == m.ImportBatch.Status.PREVIEWED
        if previewed:
            batch.status = m.ImportBatch.Status.REJECTED
            batch.problems = [
                {
                    "kind": "error",
                    "file": "",
                    "row": 0,
                    "code": "discarded",
                    "message": "Predogled je zavrgla pooblaščena oseba.",
                }
            ]
            batch.save(update_fields=["status", "problems"])
        m.ImportUpload.objects.filter(batch=batch).delete()
    if not previewed:
        messages.error(
            request,
            f"Zavrženje ni bilo izvedeno: serija je že v stanju »{batch.get_status_display()}«.",
        )
        return redirect("ui-import-batch", batch_id=batch.pk)
    messages.success(request, "Predogled je zavržen; nič ni bilo spremenjeno.")
    return redirect("ui-import")
