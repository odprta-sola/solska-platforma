from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("allauth.account.urls")),
    path("admin/", admin.site.urls),
    path("p0/api/v1/", include("core.urls")),
    path("p0/api/v1/", include("registry.urls")),
]
