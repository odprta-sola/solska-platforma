from django.conf import settings
from django.contrib import admin
from django.http import Http404
from django.urls import include, path, re_path


def closed(request, *args, **kwargs):
    """Samopostrežna obnova gesla je začasno izklopljena (individualni postopek pred B)."""
    raise Http404


urlpatterns = [
    # Pred allauth: zapre vse poti obnove gesla, tudi potrditev s ključem ali kodo.
    re_path(r"^accounts/password/reset/", closed),
    path("accounts/", include("allauth.account.urls")),
    path("admin/", admin.site.urls),
    path("p0/api/v1/", include("core.urls")),
    path("p0/api/v1/", include("registry.urls")),
    path("p0/", include("registry.ui_urls")),
]

# Nadomestka M1 in M2 za razvoj in pogodbene teste; nikoli v produkciji.
for module in sorted(settings.STUBS):
    urlpatterns.append(path(f"{module}/api/v1/", include(f"stubs.urls_{module}")))
