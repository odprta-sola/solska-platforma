"""Odjemalec API pogodbe za module M1 in M2 (D12, C05: klici samo prek API, tudi v istem procesu).

Modul ne uvaža `registry` ali sosednjega modula; podatke dobi prek tega odjemalca. Dva načina:

- servisni klic: Bearer žeton modula (`token=`), nikoli v imenu uporabnika;
- uporabniški klic: posredovana seja prijavljenega uporabnika (`session=UserSession`), s CSRF.

Nedosegljivost ali odgovor 5xx je `Unavailable`: zaščiteno dejanje zavrni oziroma dostavo zadrži
(ne »dovoljeno« in ne »nepotrebno«). Odgovor 4xx je `ApiError` s kodo napake iz pogodbe.
Žetonov in sej ne zapisujte v dnevnike.
"""

import http.client
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlsplit

from django.conf import settings

TIMEOUT_SECONDS = 5


class Unavailable(Exception):
    """Storitev ni dosegljiva ali je vrnila 5xx oziroma odgovor, ki ni JSON."""


class ApiError(Exception):
    """Odgovor 4xx s kodo napake iz pogodbe (npr. 403 scope_not_allowed)."""

    def __init__(self, status, code):
        super().__init__(f"{status} {code}")
        self.status, self.code = status, code


@dataclass(frozen=True)
class UserSession:
    """Seja prijavljenega uporabnika za uporabniški klic v isti namestitvi (C04/C05).

    Origin ni del seje: brskalnikov izvor (npr. https://sola.example) se ne ujema nujno z
    notranjim naslovom P0 (`P0_API_URL`). Klic je strežniški, zato Api pošlje izvor cilja;
    zaščita CSRF ostane, ker P0 preveri par piškotek in glava X-CSRFToken.
    """

    session_id: str
    csrf_token: str

    @classmethod
    def from_request(cls, request):
        return cls(
            session_id=request.COOKIES.get(settings.SESSION_COOKIE_NAME, ""),
            csrf_token=request.COOKIES.get(settings.CSRF_COOKIE_NAME, ""),
        )


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Preusmeritve se ne sledijo: urllib bi sejo, CSRF in žeton poslal tudi novemu cilju."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # urllib vrne odgovor 3xx kot HTTPError


_OPENER = urllib.request.build_opener(_NoRedirect)


class UrllibTransport:
    """Privzeti prenos HTTP (standardna knjižnica). Preusmeritev je napaka, ne nov cilj."""

    def send(self, method, url, headers, body):
        if urlsplit(url).scheme not in ("http", "https"):
            raise Unavailable("nedovoljena shema naslova")
        try:
            req = urllib.request.Request(url, data=body, method=method, headers=headers)  # noqa: S310
            with _OPENER.open(req, timeout=TIMEOUT_SECONDS) as response:
                status, raw = response.status, response.read()
        except urllib.error.HTTPError as exc:
            status, raw = exc.code, exc.read()
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError) as exc:
            raise Unavailable(type(exc).__name__) from exc
        except ValueError as exc:
            # Neveljaven naslov ali vrednost glave (npr. CRLF v piškotku); vsebine ne izpišemo.
            raise Unavailable("neveljavna zahteva") from exc
        if 300 <= status < 400:
            raise Unavailable("preusmeritev ni dovoljena")
        return status, raw


class Api:
    """Klici JSON na osnovni naslov namestitve (`P0_API_URL`)."""

    def __init__(self, base_url=None, transport=None):
        self.base_url = (base_url or settings.P0_API_URL).rstrip("/")
        parts = urlsplit(self.base_url)
        self.origin = f"{parts.scheme}://{parts.netloc}"  # izvor cilja, ne brskalnika
        self.transport = transport or UrllibTransport()

    def call(self, method, path, body=None, token=None, session=None):
        headers = {"Accept": "application/json"}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if session:
            cookies = {settings.SESSION_COOKIE_NAME: session.session_id}
            if session.csrf_token:
                cookies[settings.CSRF_COOKIE_NAME] = session.csrf_token
                headers["X-CSRFToken"] = session.csrf_token
            headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
            headers["Origin"] = self.origin
            headers["Referer"] = self.origin + "/"
        status, raw = self.transport.send(method, self.base_url + path, headers, data)
        if status >= 500:
            raise Unavailable(f"HTTP {status}")
        try:
            payload = json.loads(raw)
        except ValueError as exc:
            raise Unavailable("odgovor ni JSON") from exc
        if status >= 400:
            raise ApiError(status, payload.get("code", "") if isinstance(payload, dict) else "")
        return payload
