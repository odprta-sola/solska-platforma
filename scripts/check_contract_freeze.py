"""Preveri zamrznitev pogodbe api/openapi.yaml (D12, C16) proti zgodovini Git.

Test v p0 primerja datoteko z vrstico njene različice v api/zamrznitve.txt. Ta skript doda, česar
test brez zgodovine ne more: objavljena vrstica se ne sme spremeniti ali izginiti (samo
dodajanje), vsaka različica z oznako v<različica> mora imeti hash pogodbe na tej oznaki, sprememba
pogodbe pa zahteva novo različico.

Uporaba: python3 scripts/check_contract_freeze.py [osnovni-commit]
Brez osnovnega commita se primerjava z osnovo preskoči (oznake se preverijo vedno).
"""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = "api/openapi.yaml"
FREEZES = "api/zamrznitve.txt"


def git_show(ref, path):
    """Vsebina datoteke na commitu ali None, če je ni."""
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True, check=False
    )
    return result.stdout if result.returncode == 0 else None


def entries(text):
    """Seznam vrstic zamrznitev (brez komentarjev) in slovar različica -> hash."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    return lines, {line.split()[0]: line.split()[1] for line in lines}


def version_of(spec_bytes):
    match = re.search(r"^info:\n(?:[ \t].*\n)*?  version:\s*\"?([^\"\s]+)", spec_bytes.decode(), re.M)
    return match.group(1) if match else None


def check(base=None):
    errors = []
    current_text = (ROOT / FREEZES).read_text(encoding="utf-8")
    lines, frozen = entries(current_text)
    if len(frozen) != len(lines):
        errors.append("ista različica je v api/zamrznitve.txt zapisana večkrat")
    spec = (ROOT / SPEC).read_bytes()
    version = version_of(spec)
    digest = hashlib.sha256(spec).hexdigest()
    if frozen.get(version) != digest:
        errors.append(f"pogodba {version} se ne ujema z vrstico v api/zamrznitve.txt")

    tags = subprocess.run(
        ["git", "tag", "--list", "v*"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    for tag in tags:
        tagged = git_show(tag, SPEC)
        if tagged is None or version_of(tagged) != tag[1:]:
            continue
        if frozen.get(tag[1:]) != hashlib.sha256(tagged).hexdigest():
            errors.append(f"vrstica {tag[1:]} se ne ujema s pogodbo na oznaki {tag}")

    if base:
        old_freezes = git_show(base, FREEZES)
        old_spec = git_show(base, SPEC)
        if old_freezes is not None:
            old_lines, _ = entries(old_freezes.decode())
            missing = [line for line in old_lines if line not in lines]
            if missing:
                errors.append(f"objavljene vrstice so spremenjene ali odstranjene: {missing}")
        if old_spec is not None and old_spec != spec and version_of(old_spec) == version:
            errors.append(f"pogodba se je spremenila, različica {version} pa ne")
    return errors


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else None
    errors = check(base)
    for error in errors:
        print(f"::error::{error}")
    if not errors:
        print("Zamrznitev pogodbe je skladna.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
