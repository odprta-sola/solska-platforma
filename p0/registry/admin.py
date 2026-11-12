from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models

admin.site.register(models.Account, UserAdmin)
for m in (
    models.Person,
    models.PersonRole,
    models.Student,
    models.SchoolClass,
    models.Membership,
    models.StaffAssignment,
    models.Relationship,
    models.Approval,
    models.Grant,
    models.SourceMapping,
):
    admin.site.register(m)
admin.site.register(models.ChangeAudit)


@admin.register(models.AccessAudit)
class AccessAuditAdmin(admin.ModelAdmin):
    """Sled vpogledov je samo za branje: ni dodajanja, urejanja ali brisanja."""

    list_display = ("at", "actor", "screen", "entity_type", "entity_id")
    list_filter = ("screen", "entity_type")
    search_fields = ("entity_id",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
