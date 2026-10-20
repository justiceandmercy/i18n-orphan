"""Core scanning logic for i18n-orphan."""

import json
import re
from pathlib import Path
from typing import Iterable, List, Set

DEFAULT_SRC_EXT = {
    ".js", ".ts", ".jsx", ".tsx", ".vue", ".svelte",
    ".py", ".go", ".rb", ".php", ".html", ".svelte",
}

T_PATTERNS = [
    re.compile(r"""(?:\$?t|i18n\.t|translate|trans)\s*\(\s*['"]([^'"]+)['"]"""),
    re.compile(r"""i18nKey\s*=\s*['"]([^'"]+)['"]"""),
    re.compile(r"""\$t\s*\(\s*['"]([^'"]+)['"]"""),
]


def flatten(obj, prefix: str = "") -> Set[str]:
    """Flatten a nested dict into dotted key paths (leaves only)."""
    keys: Set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            full = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, dict):
                keys |= flatten(v, full)
            else:
                keys.add(full)
    return keys


def load_locale_keys(path: Path) -> Set[str]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return flatten(data)


def collect_locale_files(root: Path) -> List[Path]:
    if root.is_file():
        return [root]
    out = [p for p in root.rglob("*.json") if p.is_file()]
    return sorted(out)


def collect_source_files(root: Path, exts: Set[str]) -> List[Path]:
    if root.is_file():
        return [root]
    out = [p for p in root.rglob("*") if p.is_file() and p.suffix in exts]
    return sorted(out)


def extract_referenced_keys(text: str) -> Set[str]:
    found: Set[str] = set()
    for pat in T_PATTERNS:
        for m in pat.finditer(text):
            found.add(m.group(1))
    return found


def scan(locales_root: Path, src_root: Path, exts: Set[str]) -> dict:
    locale_files = collect_locale_files(locales_root)
    source_files = collect_source_files(src_root, exts)

    defined_keys: Set[str] = set()
    for lf in locale_files:
        try:
            defined_keys |= load_locale_keys(lf)
        except (json.JSONDecodeError, OSError):
            continue

    referenced_keys: Set[str] = set()
    for sf in source_files:
        try:
            referenced_keys |= extract_referenced_keys(sf.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue

    unused = sorted(defined_keys - referenced_keys)
    missing = sorted(referenced_keys - defined_keys)

    return {
        "locale_files": [str(p) for p in locale_files],
        "source_files": [str(p) for p in source_files],
        "defined": sorted(defined_keys),
        "referenced": sorted(referenced_keys),
        "unused": unused,
        "missing": missing,
    }