from django.urls import path

from . import ui

urlpatterns = [
    path("", ui.home, name="ui-home"),
    path("evidenca/osebe/", ui.persons, name="ui-persons"),
    path("evidenca/osebe/<uuid:person_id>/", ui.person_detail, name="ui-person"),
    path("evidenca/osebe/<uuid:person_id>/kontakt/", ui.contact, name="ui-contact"),
    path(
        "evidenca/osebe/<uuid:person_id>/povezave/<int:rel_id>/odvzem/",
        ui.revoke_relationship,
        name="ui-revoke-relationship",
    ),
    path(
        "evidenca/osebe/<uuid:person_id>/upravicenja/<int:grant_id>/odvzem/",
        ui.revoke_grant,
        name="ui-revoke-grant",
    ),
    path("evidenca/uvoz/", ui.import_index, name="ui-import"),
    path("evidenca/uvoz/<uuid:batch_id>/", ui.import_batch, name="ui-import-batch"),
    path("evidenca/uvoz/<uuid:batch_id>/uveljavi/", ui.import_apply, name="ui-import-apply"),
    path("evidenca/uvoz/<uuid:batch_id>/zavrzi/", ui.import_discard, name="ui-import-discard"),
]
