from __future__ import annotations

import logging

from app.content.monster_source_save_candidates import source_save_candidates
from app.content.monster_source_save_riders import common_failure_riders
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def _row(actions: str) -> dict[str, object]:
    return {"name": "Test Brute", "actions": actions}


def test_damage_save_derives_prone_rider_and_size_limit() -> None:
    try:
        actions, resources = source_save_candidates(_row(
            "Tail Slam. Strength Saving Throw: DC 14, one Large or smaller creature within 10 feet. "
            "Failure: 9 (2d6 + 2) Bludgeoning damage, and the target has the Prone condition. "
            "Success: Half damage."
        ))
        assert resources == []
        assert len(actions) == 1
        assert actions[0].success_damage == "half"
        assert len(actions[0].failure_effects) == 1
        assert actions[0].failure_effects[0].kind == "prone"
        assert actions[0].failure_effects[0].max_target_size is CreatureSize.LARGE
    except Exception:
        logger.exception("Shared Prone save-rider regression failed.")
        raise


def test_damage_save_derives_timed_condition_rider() -> None:
    try:
        actions, _ = source_save_candidates(_row(
            "Shock Wave. Constitution Saving Throw: DC 15, one creature within 30 feet. "
            "Failure: 12 (3d6 + 2) Thunder damage, and the target has the Stunned condition until the end of its next turn. "
            "Success: Half damage."
        ))
        effect = actions[0].failure_effects[0]
        assert effect.kind == "condition"
        assert effect.condition == "stunned"
        assert effect.expiry_timing == "target_turn_end"
    except Exception:
        logger.exception("Shared timed-condition save-rider regression failed.")
        raise


def test_source_owned_condition_uses_source_turn_timing() -> None:
    try:
        riders = common_failure_riders(
            "one creature within 30 feet",
            "The target has the Charmed condition until the start of the pirate’s next turn",
        )
        effect = riders["failure_effects"][0]
        assert effect.kind == "condition"
        assert effect.condition == "charmed"
        assert effect.expiry_timing == "source_turn_start"
    except Exception:
        logger.exception("Source-owned condition timing regression failed.")
        raise


def test_condition_only_save_compiles_when_timing_is_finite() -> None:
    try:
        actions, resources = source_save_candidates(_row(
            "Enthralling Panache. Wisdom Saving Throw: DC 12, one creature the pirate can see within 30 feet. "
            "Failure: The target has the Charmed condition until the start of the pirate’s next turn."
        ))
        assert resources == []
        assert len(actions) == 1
        assert actions[0].damage is None
        effect = actions[0].failure_effects[0]
        assert effect.condition == "charmed"
        assert effect.expiry_timing == "source_turn_start"
    except Exception:
        logger.exception("Finite condition-only save candidate regression failed.")
        raise


def test_multistage_condition_save_remains_uncompiled() -> None:
    try:
        actions, _ = source_save_candidates(_row(
            "Petrifying Gaze. Constitution Saving Throw: DC 11, one creature within 30 feet. "
            "First Failure: The target has the Restrained condition. Second Failure: The target has the Petrified condition."
        ))
        assert actions == []
    except Exception:
        logger.exception("Multistage save fail-closed regression failed.")
        raise


def test_pure_damage_save_remains_rider_free() -> None:
    try:
        actions, _ = source_save_candidates(_row(
            "Flame Burst. Dexterity Saving Throw: DC 13, each creature in a 15-foot Cone. "
            "Failure: 10 (3d6) Fire damage. Success: Half damage."
        ))
        assert len(actions) == 1
        assert actions[0].failure_effects == []
        assert actions[0].push_target_away_ft == 0
        assert actions[0].grapple is None
    except Exception:
        logger.exception("Pure-damage save regression failed.")
        raise


def test_bonus_action_grapple_save_compiles_with_size_range_and_escape_dc() -> None:
    try:
        row = {
            "name": "Test Stalker",
            "actions": "",
            "bonusActions": (
                "Quick Grapple. Dexterity Saving Throw: DC 13, "
                "one Medium or smaller creature the stalker can see within 10 feet. "
                "Failure: The target has the Grappled condition (escape DC 13)."
            ),
        }
        actions, resources = source_save_candidates(row)

        assert resources == []
        assert len(actions) == 1
        action = actions[0]
        assert action.name == "Quick Grapple"
        assert action.action_cost == "bonus_action"
        assert action.save_ability == "dexterity"
        assert action.dc == 13
        assert action.range_ft == 10
        assert action.target_max_size is CreatureSize.MEDIUM
        assert action.grapple is not None
        assert action.grapple.escape_dc == 13
        assert action.grapple.max_target_size is CreatureSize.MEDIUM
    except Exception:
        logger.exception("Bonus Action grapple-save candidate regression failed.")
        raise


def test_trampling_charge_compiles_as_recharge_bonus_save_with_prone() -> None:
    try:
        row = {
            "name": "Test Centaur",
            "speed": "50 ft.",
            "actions": "",
            "bonusActions": (
                "Trampling Charge (Recharge 5-6). The centaur moves up to its Speed without provoking "
                "Opportunity Attacks and can move through the spaces of Medium or smaller creatures. "
                "Each creature whose space the centaur enters is targeted once by the following effect. "
                "Strength Saving Throw: DC 14. Failure: 7 (1d6 + 4) Bludgeoning damage, "
                "and the target has the Prone condition."
            ),
        }
        actions, resources = source_save_candidates(row)
        assert len(actions) == 1
        action = actions[0]
        assert action.name == "Trampling Charge"
        assert action.action_cost == "bonus_action"
        assert action.save_ability == "strength"
        assert action.dc == 14
        assert action.range_ft == 50
        assert action.damage is not None
        assert (action.damage.count, action.damage.size, action.damage.bonus) == (1, 6, 4)
        assert action.damage_type.value == "bludgeoning"
        assert len(action.failure_effects) == 1
        assert action.failure_effects[0].kind == "prone"
        assert len(resources) == 1
        assert resources[0].recharge is not None
        assert resources[0].recharge.minimum_roll == 5
        assert action.resource_id == resources[0].id
    except Exception:
        logger.exception("Trampling Charge source compilation regression failed.")
        raise
