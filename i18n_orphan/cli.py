"""Command-line interface for i18n-orphan."""

import argparse
import json as _json
import sys
from pathlib import Path

from . import __version__
from .scanner import (
    DEFAULT_SRC_EXT,
    collect_locale_files,
    collect_source_files,
    scan,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="i18n-orphan",
        description="Find unused and missing i18n translation keys.",
    )
    p.add_argument("-l", "--locales", default="locales",
                   help="Locale directory or single JSON file (default: locales)")
    p.add_argument("-s", "--src", default="src",
                   help="Source directory or single file (default: src)")
    p.add_argument("--ext", default=None,
                   help="Comma-separated source extensions (default: common web langs)")
    p.add_argument("--format", choices=["text", "json"], default="text",
                   help="Output format (default: text)")
    p.add_argument("--strict", action="store_true",
                   help="Exit non-zero if any unused or missing key is found")
    p.add_argument("--fail-on-unused", action="store_true",
                   help="Exit non-zero only on unused keys")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    exts = DEFAULT_SRC_EXT
    if args.ext:
        exts = {e if e.startswith(".") else "." + e for e in args.ext.split(",") if e.strip()}

    locales_root = Path(args.locales)
    src_root = Path(args.src)

    if not locales_root.exists():
        print(f"error: locales path not found: {locales_root}", file=sys.stderr)
        return 2
    if not src_root.exists():
        print(f"error: src path not found: {src_root}", file=sys.stderr)
        return 2

    result = scan(locales_root, src_root, exts)

    if args.format == "json":
        print(_json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Locale files: {len(result['locale_files'])}")
        for lf in result["locale_files"]:
            print(f"  - {lf}")
        print(f"Source files:  {len(result['source_files'])}")
        print()
        print("Unused keys (defined but never referenced):")
        if result["unused"]:
            for k in result["unused"]:
                print(f"  - {k}")
        else:
            print("  (none)")
        print()
        print("Missing keys (referenced but not defined):")
        if result["missing"]:
            for k in result["missing"]:
                print(f"  - {k}")
        else:
            print("  (none)")
        print()
        print(f"Summary: {len(result['unused'])} unused, {len(result['missing'])} missing")

    if args.strict and (result["unused"] or result["missing"]):
        return 1
    if args.fail_on_unused and result["unused"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())