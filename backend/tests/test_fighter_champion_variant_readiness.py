from app.content.fighter_champion_variant_readiness import (
    audit_fighter_champion_variant_readiness,
    fighter_champion_variant_family_ready,
)


STATUSES = {
    "great-weapon-fighting": "supported",
    "graze-mastery": "supported",
    "sap-mastery": "supported",
    "vex-mastery": "supported",
    "defense-style": "supported",
    "shield-ac": "supported",
    "archery-style": "supported",
    "nick-mastery": "supported",
    "two-weapon-fighting": "supported",
    "slow-mastery": "arena_out_of_scope",
    "indomitable": "supported",
    "tactical-master": "supported",
}


def test_all_four_champion_variants_are_clean_through_level_fourteen() -> None:
    for build_id in ("great-weapon", "sword-shield", "archer", "dual-wield"):
        for level in (3, 8, 9, 10, 11, 12, 13, 14):
            assert audit_fighter_champion_variant_readiness(build_id, level, STATUSES) == []


def test_nick_and_twf_are_required_from_actual_archer_and_dual_wield_sheets() -> None:
    nick_blocked = {**STATUSES, "nick-mastery": "blocked"}
    assert audit_fighter_champion_variant_readiness("archer", 3, nick_blocked) == [
        "combat-capability-not-supported:nick-mastery:blocked",
    ]
    dual_issues = audit_fighter_champion_variant_readiness(
        "dual-wield", 3, {**nick_blocked, "two-weapon-fighting": "blocked"},
    )
    assert "combat-capability-not-supported:nick-mastery:blocked" in dual_issues
    assert "combat-capability-not-supported:two-weapon-fighting:blocked" in dual_issues


def test_fighter_nine_features_fail_closed_when_downgraded() -> None:
    issues = audit_fighter_champion_variant_readiness(
        "great-weapon", 9, {**STATUSES, "indomitable": "blocked", "tactical-master": "blocked"},
    )
    assert "combat-capability-not-supported:indomitable:blocked" in issues
    assert "combat-capability-not-supported:tactical-master:blocked" in issues


def test_level_fifteen_is_next_explicit_champion_blocker() -> None:
    assert audit_fighter_champion_variant_readiness("great-weapon", 13, STATUSES) == []
    assert audit_fighter_champion_variant_readiness("great-weapon", 14, STATUSES) == []
    issues = audit_fighter_champion_variant_readiness("great-weapon", 15, STATUSES)
    assert "combat-feature-not-automated:superior-critical" in issues


def test_no_full_champion_family_can_be_called_active_yet() -> None:
    for build_id in ("great-weapon", "sword-shield", "archer", "dual-wield"):
        assert fighter_champion_variant_family_ready(build_id, STATUSES) is False
