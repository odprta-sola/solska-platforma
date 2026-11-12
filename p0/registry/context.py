"""Kontekst predlog: ali prijavljeni uporabnik vidi zaslone evidence."""

from .ui import is_staff


def ui(request):
    return {"ui_staff": is_staff(request.user)}
