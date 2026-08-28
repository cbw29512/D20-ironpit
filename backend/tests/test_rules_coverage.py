from app.content.rules import build_rules_coverage
from app.domain.rules import RuleCoverageStatus
from app.main import get_rules_coverage


def test_rules_coverage_ids_sources_and_key_statuses_are_explicit() -> None:
    report = build_rules_coverage()
    entries = {entry.id: entry for entry in report.entries}

    assert len(entries) == len(report.entries)
    assert all(entry.sources for entry in report.entries)
    assert entries["initiative"].status is RuleCoverageStatus.PARTIAL
    assert entries["surprise"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["precombat-hide"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["rogue-ambush"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["sneak-attack"].status is RuleCoverageStatus.PARTIAL
    assert entries["range"].status is RuleCoverageStatus.PARTIAL
    assert entries["movement"].status is RuleCoverageStatus.ARENA_ASSUMPTION
    assert entries["hp-defeat"].status is RuleCoverageStatus.ARENA_ASSUMPTION
    assert entries["second-wind"].status is RuleCoverageStatus.PARTIAL
    assert entries["light-weapons"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["two-weapon-fighting"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["nick"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["sap"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["vex"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["opportunity-attacks"].status is RuleCoverageStatus.PARTIAL
    assert entries["disengage"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["search-hidden"].status is RuleCoverageStatus.IMPLEMENTED
    assert entries["hide"].status is RuleCoverageStatus.PARTIAL
    assert entries["invisible"].status is RuleCoverageStatus.PARTIAL
    assert entries["incapacitated"].status is RuleCoverageStatus.PARTIAL
    assert entries["conditions"].status is RuleCoverageStatus.PARTIAL
    assert entries["cover"].status is RuleCoverageStatus.PARTIAL
    assert entries["initiative-ties"].status is RuleCoverageStatus.ARENA_ASSUMPTION


def test_rules_coverage_endpoint_returns_same_contract() -> None:
    report = get_rules_coverage()

    assert report.ruleset == "SRD 5.2.1 subset"
    assert any(entry.id == "surprise" for entry in report.entries)
    assert any(entry.id == "precombat-hide" for entry in report.entries)
    assert any(entry.id == "rogue-ambush" for entry in report.entries)
    assert any(entry.id == "sneak-attack" for entry in report.entries)
    assert any(entry.id == "incapacitated" for entry in report.entries)
    assert any(entry.id == "death-saves" for entry in report.entries)
