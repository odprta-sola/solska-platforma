"""Meje modulov: M1 in M2 ne segata v tuje tabele; z drugimi komunicirajo prek API-ja (C05).

Preverjanje bere kodo kot AST: vsa imena v `import a, b`, `from x import y`, relativne uvoze
(razrešene glede na paket datoteke), `importlib.import_module`, `__import__` in
`apps.get_model` / `get_app_config` z literalnim imenom aplikacije. Prepovedani so `registry`,
`stubs` (nadomestki kličejo registry) in sosednji modul.

To je pomoč pri pouku in pregledu, ne varnostna meja: imena, sestavljena med izvajanjem,
`getattr` ali branje tabel s surovim SQL ostanejo na človeškem pregledu.
"""

import ast
from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[2]
# modul -> aplikacije, ki jih ne sme uporabljati neposredno
FORBIDDEN = {
    "m1": ("registry", "stubs", "m2"),
    "m2": ("registry", "stubs", "m1"),
}
IMPORT_CALLS = {"import_module", "__import__"}
APP_CALLS = {"get_model", "get_app_config", "get_models"}


def _package(path):
    """Ime paketa datoteke glede na p0 (npr. m1.views -> m1)."""
    parts = path.relative_to(ROOT).with_suffix("").parts
    return parts[:-1] if parts[-1] != "__init__" else parts[:-1]


def _call_name(func):
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def used_names(source, package=()):
    """Vsa polna imena modulov oziroma aplikacij, ki jih koda uporabi."""
    names = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = list(package[: max(0, len(package) - node.level + 1)])
                module = ".".join(base + ([node.module] if node.module else []))
            else:
                module = node.module or ""
            names.append(module)
            names += [".".join(filter(None, (module, alias.name))) for alias in node.names]
        elif isinstance(node, ast.Call) and node.args:
            first = node.args[0]
            literal = isinstance(first, ast.Constant) and isinstance(first.value, str)
            name = _call_name(node.func)
            if literal and name in IMPORT_CALLS:
                names.append(first.value)
            elif literal and name in APP_CALLS:
                names.append(first.value.split(".")[0])  # "registry" ali "registry.Person"
    return [n for n in names if n]


class ModuleBoundaryTests(SimpleTestCase):
    def test_moduli_ne_uvazajo_tujih_modelov(self):
        for module, banned in FORBIDDEN.items():
            folder = ROOT / module
            with self.subTest(module=module):
                if not folder.is_dir():
                    self.skipTest(f"Modul {module} še ne obstaja: meja ni preverjena.")
                self._check(folder, banned)

    def _check(self, folder, banned):
        for path in folder.rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            for name in used_names(source, _package(path)):
                self.assertNotIn(
                    name.split(".")[0],
                    banned,
                    f"{path.relative_to(ROOT)} uporabi {name}; uporabi API pogodbe (docs/razvijalci).",
                )

    def test_preverjanje_zna_zaznati_krsitev(self):
        cases = {
            "from registry.models import Person": "registry",
            "import os, registry.models": "registry",
            "import m2": "m2",
            "from stubs import m1": "stubs",
            "import importlib\nimportlib.import_module('registry.models')": "registry",
            "__import__('registry')": "registry",
            "from django.apps import apps\napps.get_model('registry', 'Person')": "registry",
            "from django.apps import apps\napps.get_model('registry.Person')": "registry",
            "from ... import registry": "registry",  # iz m1.sub.views: dva nivoja navzgor
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                tops = {n.split(".")[0] for n in used_names(source, ("m1", "sub"))}
                self.assertIn(expected, tops)

    def test_dovoljeni_uvozi_niso_krsitev(self):
        source = (
            "from core.api_client import Api\nfrom . import p0_client\n"
            "from django.apps import apps\napps.get_model('m1', 'Notice')\n"
        )
        tops = {n.split(".")[0] for n in used_names(source, ("m1",))}
        self.assertFalse(tops & {"registry", "stubs", "m2"}, tops)
