"""Skrbniški vmesnik Django za tehnično vzdrževanje (ne za poslovno delo z evidenco).

- Vsak prikaz zapisa ali seznama z osebnimi podatki se zapiše v sled vpogledov pred prikazom
  (zaslon `admin:<model>`); brez zapisa ni prikaza.
- Sledi (ChangeAudit, AccessAudit) sta samo za branje: dokazov ni mogoče spremeniti ali izbrisati.
- Osebe, povezav, upravičenj in potrditev ni mogoče brisati; povezave in upravičenja se ne
  dodajajo ali spreminjajo tukaj, ker odvzem gre samo prek authz (ključavnica in sled).
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models
from .ui import record_view, record_views


def _actor(request):
    return getattr(request.user, "person", None)


class AuditedAdmin(admin.ModelAdmin):
    """Zapiše vpogled pred prikazom seznama ali obrazca zapisa."""

    def _screen(self):
        return f"admin:{self.model._meta.model_name}"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        cl = getattr(response, "context_data", {}).get("cl")
        if cl is not None:  # TemplateResponse se izriše šele po vrnitvi, torej po zapisu
            ids = [obj.pk for obj in cl.result_list]
            record_views(_actor(request), self._screen(), self.model._meta.model_name, ids)
        return response

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id is not None:
            record_view(_actor(request), self._screen(), self.model._meta.model_name, object_id)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        record_view(_actor(request), self._screen(), self.model._meta.model_name, object_id)
        return super().delete_view(request, object_id, extra_context)

    def history_view(self, request, object_id, extra_context=None):
        record_view(_actor(request), self._screen(), self.model._meta.model_name, object_id)
        return super().history_view(request, object_id, extra_context)


class NoDeleteAdmin(AuditedAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class ViaAuthzAdmin(NoDeleteAdmin):
    """Samo ogled: dodajanje in odvzem gresta prek uvoza oziroma zaslonov evidence (authz)."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ReadOnlyAuditAdmin(admin.ModelAdmin):
    """Sled je samo za branje: ni dodajanja, urejanja ali brisanja."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Account)
class AccountAdmin(UserAdmin, AuditedAdmin):
    pass


admin.site.register(models.Person, NoDeleteAdmin)
admin.site.register(models.Approval, NoDeleteAdmin)
for model in (models.Relationship, models.Grant):
    admin.site.register(model, ViaAuthzAdmin)
for model in (
    models.PersonRole,
    models.Student,
    models.SchoolClass,
    models.Membership,
    models.StaffAssignment,
    models.SourceMapping,
):
    admin.site.register(model, AuditedAdmin)


@admin.register(models.ChangeAudit)
class ChangeAuditAdmin(ReadOnlyAuditAdmin):
    list_display = ("at", "actor", "action", "entity_type", "entity_id", "source")
    list_filter = ("entity_type",)
    search_fields = ("entity_id",)


@admin.register(models.AccessAudit)
class AccessAuditAdmin(ReadOnlyAuditAdmin):
    list_display = ("at", "actor", "screen", "entity_type", "entity_id")
    list_filter = ("screen", "entity_type")
    search_fields = ("entity_id",)
