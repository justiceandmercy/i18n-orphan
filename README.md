# i18n-orphan

Find translation keys defined in locale files but never referenced in source code,
and keys referenced in source code but missing from locale files.

## Description

`i18n-orphan` is a small, dependency-free CLI that scans your locale JSON files
and your source tree, then reports two kinds of problems:

- **Unused keys** — defined in a locale file but never referenced anywhere in source.
- **Missing keys** — referenced in source (via `t('...')`, `$t('...')`, etc.) but
  absent from every locale file.

It helps keep translation files small, avoids shipping dead strings, and catches
typos in translation keys before they reach users.

## Features

- Zero runtime dependencies (pure Python 3.9+).
- Flattens nested JSON locale files into dotted keys (`a.b.c`).
- Scans multiple source languages (JS/TS/JSX/TSX/Vue/Svelte/Python/Go/Ruby/PHP/HTML).
- Extracts keys from common i18n call patterns.
- Text or JSON output.
- Non-zero exit code on `--strict` for CI gating.

## Install

```sh
git clone https://github.com/yourname/i18n-orphan.git
cd i18n-orphan
pip install -e .
```

Or run directly without installing:

```sh
python -m i18n_orphan --locales locales --src src
```

## Usage

```sh
# Basic scan
i18n-orphan --locales locales --src src

# JSON output for CI
i18n-orphan -l locales -s src --format json

# Fail the build on any unused or missing key
i18n-orphan -l locales -s src --strict
```

Example output:

```
Locale files: 2  (locales/en.json, locales/de.json)
Source files:  14

Unused keys (defined but never referenced):
  - footer.legacyNotice
  - debug.internalLabel

Missing keys (referenced but not defined):
  - checkout.totalLabel

Summary: 2 unused, 1 missing
```

## License

MIT