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

# API modula: nadomestek (razvoj in pogodbeni testi, nikoli v produkciji), dokler ga ekipa ne
# izklopi s STUBS; nato pravi modul (m1/api_urls.py, m2/api_urls.py). Zasloni so pod /m1/, /m2/.
for module in ("m1", "m2"):
    api = f"stubs.urls_{module}" if module in settings.STUBS else f"{module}.api_urls"
    urlpatterns.append(path(f"{module}/api/v1/", include(api)))
    urlpatterns.append(path(f"{module}/", include(f"{module}.urls")))
