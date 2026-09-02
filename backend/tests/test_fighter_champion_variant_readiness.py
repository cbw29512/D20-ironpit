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
    "nick-mastery": "blocked",
    "two-weapon-fighting": "blocked",
    "slow-mastery": "arena_out_of_scope",
}


def test_supported_low_level_great_weapon_and_sword_shield_snapshots_are_clean() -> None:
    assert audit_fighter_champion_variant_readiness("great-weapon", 3, STATUSES) == []
    assert audit_fighter_champion_variant_readiness("sword-shield", 3, STATUSES) == []
    assert audit_fighter_champion_variant_readiness("great-weapon", 8, STATUSES) == []
    assert audit_fighter_champion_variant_readiness("sword-shield", 8, STATUSES) == []


def test_archer_is_not_ready_while_nick_on_its_actual_sheet_is_blocked() -> None:
    issues = audit_fighter_champion_variant_readiness("archer", 3, STATUSES)
    assert issues == ["combat-capability-not-supported:nick-mastery:blocked"]


def test_dual_wield_is_not_ready_while_twf_and_nick_are_blocked() -> None:
    issues = audit_fighter_champion_variant_readiness("dual-wield", 3, STATUSES)
    assert "combat-feature-not-automated:fighting-style-two-weapon-fighting" in issues
    assert "combat-capability-not-supported:nick-mastery:blocked" in issues
    assert "combat-capability-not-supported:two-weapon-fighting:blocked" in issues


def test_level_nine_and_above_stay_blocked_by_explicit_unfinished_character_features() -> None:
    issues = audit_fighter_champion_variant_readiness("great-weapon", 9, STATUSES)
    assert "combat-feature-not-automated:tactical-master" in issues


def test_no_full_champion_family_can_be_called_active_yet() -> None:
    for build_id in ("great-weapon", "sword-shield", "archer", "dual-wield"):
        assert fighter_champion_variant_family_ready(build_id, STATUSES) is False
