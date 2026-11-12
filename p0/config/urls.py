from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("allauth.account.urls")),
    path("admin/", admin.site.urls),
    path("p0/api/v1/", include("core.urls")),
    path("p0/api/v1/", include("registry.urls")),
]

if settings.ENABLE_STUBS:
    # Nadomestka M1 in M2 za razvoj in pogodbene teste; nikoli v produkciji.
    urlpatterns += [
        path("m1/api/v1/", include("stubs.urls_m1")),
        path("m2/api/v1/", include("stubs.urls_m2")),
    ]
