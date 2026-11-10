"""Universal save-damage HP-maximum reduction used by source-based draining effects.

A source card supplies damage, DC, save outcome and whether zero maximum HP kills.
The existing save, typed defense, terminal-death and fresh-fight engines own behavior.
"""
from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_damage import resolve_save_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.monsters import build_commoner
from app.domain.actions import SavingThrowAction
from app.domain.capability_effects import DiceSpec
from app.domain.capability_save_definitions import SaveCapabilityDefinition
from app.domain.encounters import EncounterCombatant
from app.domain.modifiers import ConcentrationState
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)


def _action(*, terminal: bool = False) -> SavingThrowAction:
    try:
        # No monster ID, name or edition selects this shared save effect.
        source = SaveCapabilityDefinition(
            id="synthetic-drain", name="Renamed Damage Effect",
            save_ability="constitution", dc=15, range_ft=5,
            damage=DiceSpec(count=2, size=6, bonus=3),
            damage_type=DamageType.PSYCHIC, success_damage="half",
            reduce_hit_point_maximum_on_damage=True,
            max_hp_zero_kills=terminal,
        )
        return _compile_save(source)
    except Exception:
        logger.exception("Failed to construct universal save-damage contract.")
        raise


def _target(*, max_hp: int = 40, psychic_immune: bool = False) -> EncounterCombatant:
    try:
        template = build_commoner().model_copy(update={
            "max_hp": max_hp,
            "damage_immunities": [DamageType.PSYCHIC] if psychic_immune else [],
        })
        return EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=5,
            state=build_combatant_state(template),
        )
    except Exception:
        logger.exception("Failed to prepare universal save target.")
        raise


@pytest.mark.parametrize("succeeded,expected", [(False, 15), (True, 7)])
def test_both_save_outcomes_reduce_maximum_by_resolved_damage(succeeded, expected):
    try:
        target = _target()
        action = _action()
        assert action.reduce_hit_point_maximum_on_damage
        assert not action.max_hp_zero_kills
        result = resolve_save_damage(
            target, action, FixedDiceProvider([6, 6]), succeeded=succeeded,
        )
        assert result.damage_roll is not None
        assert target.state.current_hp == 40 - expected
        assert target.state.hit_point_maximum_reduction == expected
        assert target.state.template.max_hp == 40  # source card remains immutable
    except Exception:
        logger.exception("Universal maximum-HP reduction by save result failed.")
        raise


def test_zero_maximum_is_terminal_even_when_temporary_hp_absorbs_damage():
    try:
        target = _target(max_hp=10)
        target.state.temporary_hp = 100
        action = _action(terminal=True)
        resolve_save_damage(target, action, FixedDiceProvider([6, 6]), succeeded=False)
        assert target.state.is_dead
        assert not target.state.is_alive
        assert target.state.current_hp == 0
        assert target.state.hit_point_maximum_reduction == 15
        assert target.state.template.max_hp == 10
    except Exception:
        logger.exception("Zero maximum-HP terminal test failed.")
        raise



@pytest.mark.parametrize("succeeded,maximum", [(False, 10), (True, 6)])
def test_terminal_maximum_loss_cleans_rage_and_concentration(
    succeeded: bool, maximum: int,
):
    try:
        target = _target(max_hp=maximum)
        state = target.state
        state.temporary_hp = 100  # Hit-point damage does not kill the character.
        state.active_effect_ids.append("rage")
        state.temporary_damage_resistances.append(DamageType.BLUDGEONING)
        state.concentration = ConcentrationState(
            source_id="source", effect_id="synthetic-concentration", started_round=1,
        )
        # A successful concentration save against the temporary-HP damage
        # cannot preserve concentration after maximum HP is reduced to zero.
        resolve_save_damage(
            target, _action(terminal=True), FixedDiceProvider([6, 6, 20]),
            succeeded=succeeded, affected_states=[state],
        )
        assert state.is_dead
        assert state.concentration is None
        assert "rage" not in state.active_effect_ids
        assert DamageType.BLUDGEONING not in state.temporary_damage_resistances
        assert state.template.max_hp == maximum
    except Exception:
        logger.exception("Terminal maximum-HP cleanup failed after save damage.")
        raise


def test_typed_immunity_prevents_damage_linked_maximum_hp_reduction():
    try:
        target = _target(psychic_immune=True)
        resolve_save_damage(target, _action(), FixedDiceProvider([6, 6]), succeeded=False)
        assert target.state.current_hp == 40
        assert target.state.hit_point_maximum_reduction == 0
    except Exception:
        logger.exception("Typed immune save-damage maximum-HP guard failed.")
        raise


def test_schema_fails_closed_on_unbacked_terminal_or_conflicting_save_flags():
    try:
        with pytest.raises(ValidationError):
            SaveCapabilityDefinition(
                id="bad", name="No damage", save_ability="constitution",
                dc=12, range_ft=5, reduce_hit_point_maximum_on_damage=True,
            )
        with pytest.raises(ValidationError):
            SaveCapabilityDefinition(
                id="bad", name="No reduction", save_ability="constitution",
                dc=12, range_ft=5, max_hp_zero_kills=True,
            )
        with pytest.raises(ValidationError):
            SavingThrowAction(
                id="bad", name="Conflicting reducers", save_ability="constitution",
                dc=12, range_ft=5, damage_dice_count=1, damage_type="psychic",
                reduce_hit_point_maximum_on_failed_save=True,
                reduce_hit_point_maximum_on_damage=True,
            )
    except Exception:
        logger.exception("Universal save schema fail-closed test failed.")
        raise
