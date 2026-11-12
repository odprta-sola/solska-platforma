"""Meje modulov: M1 in M2 ne segata v tuje tabele; z drugimi komunicirajo prek API-ja.

Če mape modula še ni, test ne preverja ničesar (nadomestka M1/M2 sta v `stubs`).
"""

import re
from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[2]
IMPORT = re.compile(r"^\s*(?:from|import)\s+([\w.]+)", re.MULTILINE)
# modul -> predpone, ki jih ne sme uvažati
FORBIDDEN = {
    "m1": ("registry", "m2"),
    "m2": ("registry", "m1"),
}


class ModuleBoundaryTests(SimpleTestCase):
    def test_moduli_ne_uvazajo_tujih_modelov(self):
        for module, banned in FORBIDDEN.items():
            folder = ROOT / module
            if not folder.is_dir():
                continue
            for path in folder.rglob("*.py"):
                for name in IMPORT.findall(path.read_text(encoding="utf-8")):
                    top = name.split(".")[0]
                    self.assertNotIn(
                        top,
                        banned,
                        f"{path.relative_to(ROOT)} uvaža {name}; uporabi API pogodbe (docs/razvijalci).",
                    )

    def test_preverjanje_zna_zaznati_kršitev(self):
        self.assertEqual(
            IMPORT.findall("from registry.models import Person\nimport m2\n"),
            ["registry.models", "m2"],
        )
