"""Pomoč za teste modulov: prenos odjemalca API skozi Django testnega odjemalca (brez omrežja).

Zahteva gre skozi vse vmesne plasti (seja, CSRF, napake API), kot bi prišla po HTTP.
Uporaba: `Api(transport=DjangoClientTransport())`.
"""

from http.cookies import SimpleCookie
from urllib.parse import urlsplit

from django.test import Client


class DjangoClientTransport:
    def __init__(self):
        self.requests = []  # (metoda, pot, glave) za preverjanje v testih

    def send(self, method, url, headers, body):
        parts = urlsplit(url)
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        self.requests.append((method, parts.path, dict(headers)))
        client = Client(enforce_csrf_checks=True)
        if "Cookie" in headers:
            for key, morsel in SimpleCookie(headers["Cookie"]).items():
                client.cookies[key] = morsel.value
        extra = {
            f"HTTP_{name.upper().replace('-', '_')}": value
            for name, value in headers.items()
            if name in ("Authorization", "X-CSRFToken", "Origin", "Referer", "Accept")
        }
        if method == "GET":
            response = client.get(path, **extra)
        else:
            response = getattr(client, method.lower())(
                path, data=body or b"", content_type=headers.get("Content-Type", ""), **extra
            )
        return response.status_code, response.content
