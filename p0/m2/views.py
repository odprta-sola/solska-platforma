"""Zasloni M2 eSoglasja.

Začetni zaslon je vzorec: identiteta pride iz P0 prek API z uporabnikovo sejo.

Ekipa m2 doda svoje zaslone po istem vzorcu: prijava (seja P0), klic prek `p0_client`,
ob `Unavailable` zavrnitev dejanja (503), nikoli tiho »dovoljeno«.
"""

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .p0_client import ApiError, Client, Unavailable, UserSession


def client():
    """Odjemalec za ta zahtevek (testi ga zamenjajo s prenosom brez omrežja)."""
    return Client()


@require_GET
def home(request):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    try:
        me = client().me(UserSession.from_request(request))
    except Unavailable:
        return render(request, "m2/nedosegljivo.html", status=503)
    except ApiError as exc:
        return render(request, "m2/nedosegljivo.html", status=exc.status)
    return render(request, "m2/zacetek.html", {"me": me})
