"""Focused regressions for the documentation guard."""
from pathlib import Path

from scripts.check_documentation_authority import broken_links, indexed_files


def test_index_detects_duplicate_rows_and_preserves_roles():
    index = """# Documentation map
| File | Role |
|---|---|
| `AGENTS.md` | operating |
| `docs/audit.md` | historical evidence |
| `AGENTS.md` | operating |
"""
    paths, duplicates = indexed_files(index)
    assert paths == {"AGENTS.md", "docs/audit.md"}
    assert duplicates == ["AGENTS.md"]


def test_local_links_validate_without_fetching_external_urls(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "AGENTS.md").write_text("# Agents", encoding="utf-8")
    body = "[working](../AGENTS.md) [external](https://example.com) [missing](NOPE.md)"
    assert broken_links(tmp_path, "docs/check.md", body) == [
        "docs/check.md: NOPE.md",
    ]


def test_local_links_reject_path_escape(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    assert broken_links(tmp_path, "docs/check.md", "[escape](../../etc/passwd)") == [
        "docs/check.md: ../../etc/passwd",
    ]
