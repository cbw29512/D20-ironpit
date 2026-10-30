from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_limited_use_source_audit import limited_use_issues, parse_limited_use_names
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.combatants import RechargeRule, ResourceDefinition

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_recharge_marker_is_fingerprinted_with_source_section() -> None:
    assert parse_limited_use_names(_row("Gold Dragon Wyrmling")) == [
        "actions:Fire Breath (Recharge 5-6)",
    ]


def test_per_day_marker_is_fingerprinted_with_source_section() -> None:
    assert parse_limited_use_names(_row("Gnoll Warrior")) == ["bonusActions:Rampage (1/Day)"]


def test_current_saber_tooth_has_no_limited_use_feature() -> None:
    saber = _monster("Saber-Toothed Tiger")
    assert saber.source_limited_use_names == []
    assert limited_use_issues(saber, _row("Saber-Toothed Tiger")) == []


def test_unimplemented_recharge_economy_fails_closed() -> None:
    wolf = _monster("Wolf")
    row = dict(_row("Wolf"))
    row["actions"] = "Howl (Recharge 5-6). Wisdom Saving Throw: DC 12. Failure: Frightened."
    expected = ["actions:Howl (Recharge 5-6)"]
    drifted = wolf.model_copy(update={"source_limited_use_names": expected})
    issues = limited_use_issues(drifted, row)
    assert "uncertified-limited-use:actions-howl-recharge-5-6" in issues


def test_source_derived_ape_recharge_is_bound_and_certified() -> None:
    ape = _monster("Ape")
    row = _row("Ape")
    rock = next(attack for attack in ape.alternate_weapon_attacks if attack.weapon.name == "Rock")

    assert ape.source_limited_use_names == ["actions:Rock (Recharge 6)"]
    assert rock.resource_id == "ape-rock-recharge"
    assert ape.attack_action is not None
    assert [slot.attack_ids for slot in ape.attack_action.slots] == [["ape-fist"], ["ape-fist"]]
    assert limited_use_issues(ape, row) == []
    assert audit_monster_source(ape, row) == []


def test_recharge_threshold_mismatch_still_fails_closed() -> None:
    ape = _monster("Ape")
    definition = ape.resources[0]
    wrong_rule = RechargeRule(minimum_roll=5)
    drifted = ape.model_copy(update={
        "resources": [definition.model_copy(update={"recharge": wrong_rule})],
    })

    assert "uncertified-limited-use:actions-rock-recharge-6" in limited_use_issues(drifted, _row("Ape"))


def test_limited_use_fingerprint_drift_is_detected() -> None:
    wolf = _monster("Wolf").model_copy(update={"source_limited_use_names": ["actions:Howl (Recharge 5-6)"]})
    assert "source-limited-use-fingerprint-mismatch" in limited_use_issues(wolf, _row("Wolf"))


def _daily_gaze(section: str, action_cost: str):
    try:
        basilisk = _monster("Basilisk")
        gaze = next(action for action in basilisk.saving_throw_actions if action.name == "Petrifying Gaze")
        resource = ResourceDefinition(id="daily-gaze", name="Petrifying Gaze", max_uses=2)
        action = gaze.model_copy(update={
            "resource_id": resource.id,
            "resource_cost": 1,
            "action_cost": action_cost,
        })
        fingerprint = f"{section}:Petrifying Gaze (2/Day)"
        template = basilisk.model_copy(update={
            "saving_throw_actions": [action],
            "resources": [resource],
            "source_limited_use_names": [fingerprint],
        })
        row = {"traits": "", "actions": "", "bonusActions": "", "reactions": ""}
        source_field = {"actions": "actions", "bonusActions": "bonusActions", "reactions": "reactions"}[section]
        row[source_field] = "Petrifying Gaze (2/Day)."
        return template, row
    except Exception:
        logger.exception("Failed to build synthetic daily-use audit fixture.")
        raise


def test_bonus_action_daily_resource_matches_source_action_economy() -> None:
    try:
        template, row = _daily_gaze("bonusActions", "bonus_action")
        assert limited_use_issues(template, row) == []
    except Exception:
        logger.exception("Bonus-action daily resource audit regression failed.")
        raise


def test_reaction_daily_resource_matches_source_action_economy() -> None:
    try:
        template, row = _daily_gaze("reactions", "reaction")
        assert limited_use_issues(template, row) == []
    except Exception:
        logger.exception("Reaction daily resource audit regression failed.")
        raise


def test_daily_resource_in_wrong_action_economy_section_fails_closed() -> None:
    try:
        template, row = _daily_gaze("bonusActions", "action")
        issues = limited_use_issues(template, row)
        assert "uncertified-limited-use:bonusactions-petrifying-gaze-2-day" in issues
    except Exception:
        logger.exception("Daily resource action-economy mismatch regression failed.")
        raise


def test_arena_neutral_bonus_action_recharge_does_not_require_runtime_resource() -> None:
    try:
        blink = _monster("Blink Dog")
        assert blink.source_limited_use_names == ["bonusActions:Teleport (Recharge 4-6)"]
        assert limited_use_issues(blink, _row("Blink Dog")) == []
    except Exception:
        logger.exception("Arena-neutral limited-use Bonus Action regression failed.")
        raise


def test_animate_trees_is_unavailable_without_default_arena_trees() -> None:
    try:
        treant = _monster("Treant")
        row = _row("Treant")
        assert treant.source_limited_use_names == ["actions:Animate Trees (1/Day)"]
        assert limited_use_issues(treant, row) == []
        assert audit_monster_source(treant, row) == []
    except Exception:
        logger.exception("Treant ambient-tree arena policy regression failed.")
        raise
