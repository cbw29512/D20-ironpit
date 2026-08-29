from app.main import version


def test_version_reports_render_commit(monkeypatch) -> None:
    monkeypatch.setenv("RENDER_GIT_COMMIT", "abc123")
    assert version() == {"commit": "abc123"}


def test_version_uses_local_fallback(monkeypatch) -> None:
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)
    assert version() == {"commit": "local"}
