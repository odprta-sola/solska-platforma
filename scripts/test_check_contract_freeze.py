"""Scenariji za scripts/check_contract_freeze.py v začasnem repozitoriju Git.

Zagon: python3 -m unittest scripts/test_check_contract_freeze.py
"""

import hashlib
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check_contract_freeze.py"
SPEC = 'openapi: 3.1.0\ninfo:\n  title: t\n  version: {v}\n  description: x\npaths: {{}}\n'


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


class FreezeCheckTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        (self.root / "api").mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        self.write(SPEC.format(v="1.0.0"), [("1.0.0", SPEC.format(v="1.0.0"))])
        self.base = self.commit("1.0.0")
        self.git("tag", "v1.0.0")
        spec = importlib.util.spec_from_file_location("freeze", SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.mod.ROOT = self.root

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def write(self, spec, rows):
        (self.root / "api" / "openapi.yaml").write_text(spec)
        lines = ["# komentar"] + [f"{v} {sha(s)} 2026-11-13 naročnik" for v, s in rows]
        (self.root / "api" / "zamrznitve.txt").write_text("\n".join(lines) + "\n")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def test_nespremenjeno_je_skladno(self):
        self.assertEqual(self.mod.check(self.base), [])

    def test_nova_razlicica_z_novo_vrstico_je_skladna(self):
        v1, v2 = SPEC.format(v="1.0.0"), SPEC.format(v="1.1.0") + "# nova pot\n"
        self.write(v2, [("1.0.0", v1), ("1.1.0", v2)])
        self.assertEqual(self.mod.check(self.base), [])

    def test_sprememba_brez_nove_vrstice_pade(self):
        changed = SPEC.format(v="1.0.0") + "# komentar\n"
        (self.root / "api" / "openapi.yaml").write_text(changed)
        self.assertTrue(self.mod.check(self.base))

    def test_prepisan_hash_obstojece_vrstice_pade(self):
        # Nasprotni primer tretjega pregleda (OA T-03, DS T-06): test v p0 bi tu uspel.
        changed = SPEC.format(v="1.0.0") + "# komentar\n"
        self.write(changed, [("1.0.0", changed)])
        errors = self.mod.check(self.base)
        self.assertTrue(any("objavljene vrstice" in e for e in errors))
        self.assertTrue(any("oznaki v1.0.0" in e for e in errors))
        self.assertTrue(any("različica 1.0.0 pa ne" in e for e in errors))

    def test_prepis_pade_tudi_brez_osnove_zaradi_oznake(self):
        changed = SPEC.format(v="1.0.0") + "# komentar\n"
        self.write(changed, [("1.0.0", changed)])
        self.assertTrue(any("oznaki v1.0.0" in e for e in self.mod.check(None)))

    def test_nova_razlicica_brez_vrstice_pade(self):
        (self.root / "api" / "openapi.yaml").write_text(SPEC.format(v="1.1.0"))
        self.assertTrue(any("ne ujema z vrstico" in e for e in self.mod.check(None)))

    def test_odstranjena_vrstica_pade(self):
        v2 = SPEC.format(v="1.1.0")
        self.write(v2, [("1.1.0", v2)])
        self.assertTrue(any("objavljene vrstice" in e for e in self.mod.check(self.base)))

    def test_podvojena_razlicica_pade(self):
        v1 = SPEC.format(v="1.0.0")
        self.write(v1, [("1.0.0", v1), ("1.0.0", v1 + "x")])
        self.assertTrue(any("večkrat" in e for e in self.mod.check(self.base)))


if __name__ == "__main__":
    unittest.main()
