"""Varovala nastavitev, ki se preverijo ob nalaganju (tudi pod gunicorn, brez manage.py check)."""


def stubs_in_production(debug, stubs):
    """Nadomestka M1/M2 sta samo za razvoj in teste; brez DEBUG zagon ni dovoljen."""
    return bool(stubs) and not debug
