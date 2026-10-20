"""Architectural hygiene is enforced regardless of production file length."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_source_limits as limits


def test_large_cohesive_module_is_not_rejected(tmp_path, monkeypatch):
    module = tmp_path / "combat_mechanic.py"
    module.write_text("value = 1\n" * 250, encoding="utf-8")
    monkeypatch.setattr(limits, "production_files", lambda: [module])
    monkeypatch.setattr(limits, "enforce_repository_hygiene", lambda: None)
    limits.main()


def test_removed_legacy_files_still_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "backend").mkdir()
    (tmp_path / "backend" / "pyproject.toml").write_text("", encoding="utf-8")
    (tmp_path / "docker-compose.yml").write_text("legacy", encoding="utf-8")
    try:
        limits.enforce_repository_hygiene()
    except RuntimeError as exc:
        assert "Removed legacy files returned" in str(exc)
    else:
        raise AssertionError("Legacy architecture guard must remain enforced")
