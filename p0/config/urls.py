from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("allauth.account.urls")),
    path("admin/", admin.site.urls),
    path("p0/api/v1/", include("core.urls")),
    path("p0/api/v1/", include("registry.urls")),
]

# Nadomestka M1 in M2 za razvoj in pogodbene teste; nikoli v produkciji.
for module in sorted(settings.STUBS):
    urlpatterns.append(path(f"{module}/api/v1/", include(f"stubs.urls_{module}")))
