"""Universal persistent failed-save curse + healing-block lifecycle."""
from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.restoration_riders import apply_restoration_riders
from app.combat.zero_hp import restore_hit_points
from app.content.shared_restoration_spells_2014 import remove_curse_2014
from app.domain.encounters import EncounterCombatant
from app.domain.on_hit_conditions import OnHitConditionSave
from test_on_hit_condition_save import _attacker, _target

logger = logging.getLogger(__name__)


def _persistent_curse(dc: int = 12, *, effect_id: str = "synthetic-rot") -> OnHitConditionSave:
    try:
        return OnHitConditionSave(
            save_ability="constitution",
            dc=dc,
            effect_id=effect_id,
            curse_id=effect_id,
            cannot_regain_hit_points=True,
            allowed_removal_action_ids=["remove-curse"],
            delayed_max_hp_reduction_delay_hours=24,
            delayed_max_hp_reduction_dice_count=3,
            delayed_max_hp_reduction_dice_size=6,
            delayed_max_hp_reduction_zero_kills=True,
        )
    except Exception:
        logger.exception("Failed to build synthetic persistent curse effect.")
        raise


def _failed_hit(effect: OnHitConditionSave):
    try:
        attacker, attack = _attacker(effect)
        target = _target(save_ability="constitution")
        event = resolve_attack(
            1, 1, attacker, target, attack, 5,
            FixedDiceProvider([15, 4, 4, 1]),
            spend_action=False,
            actor_event_id="renamed-source",
            target_event_id="renamed-target",
        )
        return target, event
    except Exception:
        logger.exception("Failed to resolve synthetic persistent curse hit.")
        raise


def test_failed_save_applies_source_neutral_curse_and_blocks_healing() -> None:
    try:
        target, event = _failed_hit(_persistent_curse())
        assert event.save_succeeded is False
        assert "synthetic-rot" in target.active_effect_ids
        assert target.active_curses == ["synthetic-rot"]
        effect = next(item for item in target.timed_effects if item.effect_id == "synthetic-rot")
        assert effect.owned_curse_ids == ["synthetic-rot"]
        assert effect.cannot_regain_hit_points is True
        assert effect.allowed_removal_action_ids == ["remove-curse"]
        assert target.hit_point_maximum_reduction == 0

        target.current_hp = max(1, target.current_hp - 5)
        hp_before = target.current_hp
        assert restore_hit_points(target, 5) == 0
        assert target.current_hp == hp_before
    except Exception:
        logger.exception("Persistent curse healing-block regression failed.")
        raise


def test_successful_save_does_not_apply_persistent_effect() -> None:
    try:
        effect = _persistent_curse(effect_id="renamed-curse")
        attacker, attack = _attacker(effect)
        target = _target(save_ability="constitution")
        event = resolve_attack(
            1, 1, attacker, target, attack, 5,
            FixedDiceProvider([15, 4, 4, 20]),
            spend_action=False,
            actor_event_id="unrelated-source",
            target_event_id="unrelated-target",
        )
        assert event.save_succeeded is True
        assert "renamed-curse" not in target.active_effect_ids
        assert target.active_curses == []
        assert target.timed_effects == []
    except Exception:
        logger.exception("Persistent curse successful-save regression failed.")
        raise


def test_remove_curse_cleans_owned_effect_and_restores_healing() -> None:
    try:
        target_state, _ = _failed_hit(_persistent_curse(effect_id="generic-curse"))
        target_state.current_hp = max(1, target_state.current_hp - 5)
        target = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=5, state=target_state,
        )
        applied = apply_restoration_riders(target, remove_curse_2014(), ["curse"])
        assert applied == ["curse"]
        assert target.state.active_curses == []
        assert "generic-curse" not in target.state.active_effect_ids
        assert target.state.timed_effects == []
        assert restore_hit_points(target.state, 5) == 5
    except Exception:
        logger.exception("Persistent curse removal regression failed.")
        raise
