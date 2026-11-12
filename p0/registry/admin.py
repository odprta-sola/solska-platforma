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
