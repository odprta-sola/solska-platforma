"""Preveri lokalne Markdown povezave in GitHub sidra; zunanjih URL ne preverja."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def clean(text):
    return re.sub(r"^\`{3,}.*?^\`{3,}[^\n]*", "", text, flags=re.M | re.S)

def anchors(text):
    found, counts = set(), {}
    for title in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", clean(text), re.M):
        title = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", title)
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        n = counts.get(slug, 0)
        counts[slug] = n + 1
        found.add(slug if n == 0 else f"{slug}-{n}")
    found.update(re.findall(r'\b(?:id|name)=["\']([^"\']+)["\']', text))
    return found

def check(root):
    errors = []
    for source in sorted(root.rglob("*.md")):
        if ".git" in source.parts:
            continue
        text = clean(source.read_text(encoding="utf-8"))
        targets = re.findall(r"!?\[[^]\n]*\]\(<?([^\s)>]+)>?(?:\s+[^)]*)?\)", text)
        targets += re.findall(r"^\s*\[[^]]+\]:\s*<?([^\s>]+)", text, re.M)
        for target in targets:
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            dest = (root / unquote(url.path).lstrip("/")) if url.path.startswith("/") else source.parent / unquote(url.path)
            if not url.path:
                dest = source
            if not dest.exists():
                errors.append(f"{source.relative_to(root)}: manjka {target}")
            elif url.fragment and dest.suffix.lower() == ".md":
                if unquote(url.fragment) not in anchors(dest.read_text(encoding="utf-8")):
                    errors.append(f"{source.relative_to(root)}: neveljavno sidro {target}")
    return errors

if __name__ == "__main__":
    errors = check(ROOT)
    print("\n".join(errors) if errors else "Notranje povezave in sidra so veljavni.")
    sys.exit(bool(errors))
