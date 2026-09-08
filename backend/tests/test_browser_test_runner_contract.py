from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / ".github" / "workflows" / "ci.yml"
RUNNER = ROOT / "scripts" / "run_browser_tests.sh"
CHAINED = {
    "browser-fighter6.test.cjs",
    "browser-fighter7.test.cjs",
    "browser-fighter8.test.cjs",
}


def test_ci_uses_the_discovery_based_browser_test_runner() -> None:
    ci_text = CI.read_text(encoding="utf-8")
    assert "bash scripts/run_browser_tests.sh" in ci_text


def test_runner_discovers_all_tests_and_excludes_only_chained_suites() -> None:
    runner_text = RUNNER.read_text(encoding="utf-8")
    assert "frontend/*.test.cjs" in runner_text
    for chained_name in CHAINED:
        assert chained_name in runner_text

    test_names = {path.name for path in (ROOT / "frontend").glob("*.test.cjs")}
    assert CHAINED < test_names
    independent_names = test_names - CHAINED
    assert independent_names
