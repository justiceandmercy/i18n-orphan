import json
import tempfile
from pathlib import Path

from i18n_orphan.scanner import scan, flatten


def test_flatten_nested():
    data = {"a": {"b": "x", "c": {"d": "y"}}, "e": "z"}
    assert flatten(data) == {"a.b", "a.c.d", "e"}


def test_scan_finds_unused_and_missing():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "locales").mkdir()
        (root / "src").mkdir()
        (root / "locales" / "en.json").write_text(
            json.dumps({"used": "u", "unused": "x", "nested": {"a": "b", "b": "c"}})
        )
        (root / "src" / "app.js").write_text('t("used"); t("missing.key"); t("nested.a");')
        res = scan(root / "locales", root / "src", {".js"})
        assert "unused" in res["unused"]
        assert "nested.b" in res["unused"]
        assert "missing.key" in res["missing"]
        assert "used" not in res["unused"]
        assert "nested.a" not in res["unused"]