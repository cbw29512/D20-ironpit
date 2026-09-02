from __future__ import annotations

from app.content.combat_build_choice_overlays import FIGHTER_COMBAT_BUILD_CHOICES
from app.content.combat_engine_coverage import audit_build_capability_contract, audit_current_build_capabilities


def _fighter_statuses() -> dict[str, str]:
    return {
        "great-weapon-fighting": "supported",
        "graze-mastery": "supported",
        "sap-mastery": "supported",
        "defense-style": "supported",
        "shield-ac": "supported",
        "archery-style": "supported",
        "vex-mastery": "supported",
        "nick-mastery": "supported",
        "two-weapon-fighting": "supported",
        "slow-mastery": "arena_out_of_scope",
    }


def _fighter_build_statuses() -> dict[tuple[str, str], str]:
    active = {"great-weapon", "sword-shield"}
    return {
        ("fighter", build_id): "active" if build_id in active else "planned"
        for build_id in FIGHTER_COMBAT_BUILD_CHOICES
    }


def test_current_fighter_overlays_accept_explicit_supported_and_arena_statuses() -> None:
    assert audit_current_build_capabilities(_fighter_statuses()) == []


def test_missing_required_capability_fails_closed() -> None:
    statuses = _fighter_statuses()
    statuses.pop("graze-mastery")

    issues = audit_build_capability_contract(
        FIGHTER_COMBAT_BUILD_CHOICES.values(), statuses, _fighter_build_statuses(),
    )

    assert any("graze-mastery" in issue and "must be supported or blocked" in issue for issue in issues)


def test_active_build_cannot_depend_on_blocked_capability() -> None:
    statuses = _fighter_statuses()
    statuses["graze-mastery"] = "blocked"

    issues = audit_build_capability_contract(
        FIGHTER_COMBAT_BUILD_CHOICES.values(), statuses, _fighter_build_statuses(),
    )

    assert any("active build requires 'graze-mastery'" in issue for issue in issues)


def test_active_sword_shield_cannot_depend_on_blocked_shield_ac() -> None:
    statuses = _fighter_statuses()
    statuses["shield-ac"] = "blocked"

    issues = audit_build_capability_contract(
        FIGHTER_COMBAT_BUILD_CHOICES.values(), statuses, _fighter_build_statuses(),
    )

    assert any("active build requires 'shield-ac'" in issue for issue in issues)


def test_supported_nick_and_twf_can_still_be_downgraded_fail_closed() -> None:
    statuses = _fighter_statuses()
    statuses["nick-mastery"] = "blocked"
    statuses["two-weapon-fighting"] = "blocked"
    build_statuses = _fighter_build_statuses()
    build_statuses[("fighter", "dual-wield")] = "active"

    issues = audit_build_capability_contract(
        FIGHTER_COMBAT_BUILD_CHOICES.values(), statuses, build_statuses,
    )

    assert any("active build requires 'nick-mastery'" in issue for issue in issues)
    assert any("active build requires 'two-weapon-fighting'" in issue for issue in issues)


def test_partial_status_is_not_valid_for_declared_build_requirement() -> None:
    statuses = _fighter_statuses()
    statuses["graze-mastery"] = "partial"

    issues = audit_build_capability_contract(
        FIGHTER_COMBAT_BUILD_CHOICES.values(), statuses, _fighter_build_statuses(),
    )

    assert any("graze-mastery" in issue and "must be supported or blocked" in issue for issue in issues)


def test_arena_ignored_capability_must_be_explicitly_out_of_scope() -> None:
    statuses = _fighter_statuses()
    statuses["slow-mastery"] = "blocked"

    issues = audit_build_capability_contract(
        FIGHTER_COMBAT_BUILD_CHOICES.values(), statuses, _fighter_build_statuses(),
    )

    assert any("slow-mastery" in issue and "arena_out_of_scope" in issue for issue in issues)
