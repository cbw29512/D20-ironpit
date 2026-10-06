from __future__ import annotations

import logging

from app.combat.barbarian import rage_active
from app.combat.condition_rules import automatically_fails_strength_dexterity_save
from app.combat.danger_sense import danger_sense_advantage
from app.combat.defensive_modifier_rules import (
    consume_saving_throw_modifiers,
    saving_throw_advantage_sources,
    saving_throw_disadvantage_sources as modifier_save_disadvantage_sources,
)
from app.combat.d20_bonus_dice import apply_d20_bonus_die_if_useful, apply_resource_backed_d20_bonus_if_useful
from app.combat.d20_outcome_adjustments import apply_resource_backed_d20_outcome_adjustment_if_useful
from app.combat.dice import DiceProvider
from app.combat.dodge import dodge_dex_save_advantage_sources
from app.combat.exhaustion import saving_throw_disadvantage_sources
from app.combat.failed_d20_test_override import apply_failed_d20_test_override
from app.combat.save_success_override import apply_save_success_override
from app.combat.failed_save_reroll import apply_failed_save_reroll
from app.combat.grapple import RESTRAINED_EFFECT_ID
from app.combat.timed_ability_d20 import timed_ability_d20_disadvantage_sources
from app.combat.modifier_stack import apply_d20_bonus_dice, saving_throw_flat_bonus
from app.combat.rolls import roll_d20
from app.combat.saving_throw_minimum import apply_saving_throw_minimum
from app.combat.saving_throw_traits import sure_footed_advantage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import CombatantState, DiceRoll, RollMode, RollRevision
from app.domain.modifiers import ModifierKind
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def saving_throw_mode(
    state: CombatantState,
    ability: str,
    context: SavingThrowContext | None = None,
) -> RollMode:
    try:
        advantage = (
            int(ability == "strength" and rage_active(state))
            + danger_sense_advantage(state, ability)
            + dodge_dex_save_advantage_sources(state, ability)
            + sure_footed_advantage(state, ability, context)
            + saving_throw_advantage_sources(state, ability, context)
            + len(context.advantage_sources if context is not None else ())
        )
        disadvantage = (
            saving_throw_disadvantage_sources(state)
            + modifier_save_disadvantage_sources(state, ability)
            + timed_ability_d20_disadvantage_sources(state, ability)
            + len(context.disadvantage_sources if context is not None else ())
        )
        if ability == "dexterity" and RESTRAINED_EFFECT_ID in state.active_effect_ids:
            disadvantage += 1
        if (advantage > 0) == (disadvantage > 0):
            return RollMode.NORMAL
        return RollMode.ADVANTAGE if advantage else RollMode.DISADVANTAGE
    except Exception as exc:
        logger.exception("Failed to resolve saving-throw mode for %s.", state.template.name)
        raise RuntimeError("Saving-throw mode could not be resolved.") from exc


def _indomitable_revision(original: DiceRoll, replacement: DiceRoll) -> RollRevision:
    try:
        return RollRevision(
            source_effect_id="indomitable",
            kind="full_reroll",
            original_rolls=list(original.rolls),
            replacement_rolls=list(replacement.rolls),
            original_modifier=original.modifier,
            replacement_modifier=replacement.modifier,
            original_selected=original.selected_roll,
            replacement_selected=replacement.selected_roll,
            original_total=original.total,
            replacement_total=replacement.total,
            accepted="replacement",
        )
    except Exception as exc:
        logger.exception("Failed to build Indomitable revision evidence.")
        raise RuntimeError("Indomitable revision could not be recorded.") from exc


def resolve_saving_throw(
    state: CombatantState,
    ability: str,
    dc: int,
    dice: DiceProvider,
    context: SavingThrowContext | None = None,
    *,
    round_number: int | None = None,
    encounter_roller: EncounterCombatant | None = None,
    setup: EncounterSetup | None = None,
) -> tuple[DiceRoll | None, bool]:
    try:
        if ability in {"strength", "dexterity"} and automatically_fails_strength_dexterity_save(state):
            consume_saving_throw_modifiers(state)
            return None, False
        if ability not in state.template.saving_throw_bonuses:
            raise ValueError(f"{state.template.name} lacks a certified {ability.title()} saving throw bonus.")
        modifier = state.template.saving_throw_bonuses[ability] + saving_throw_flat_bonus(state, ability)
        roll = apply_d20_bonus_dice(
            state,
            ModifierKind.SAVING_THROW_BONUS_DIE,
            roll_d20(dice, modifier, saving_throw_mode(state, ability, context)),
            dice,
        )
        consume_saving_throw_modifiers(state)
        if state.active_d20_bonus_dice:
            if round_number is None:
                round_number = state.current_round
            if round_number is None:
                raise ValueError("Active d20 bonus die requires saving-throw round context.")
            roll, _ = apply_d20_bonus_die_if_useful(
                state, "saving_throw", roll, dc, dice, round_number,
            )
        if state.template.progression_features.resource_backed_d20_bonus_dice:
            roll, _ = apply_resource_backed_d20_bonus_if_useful(
                state, "saving_throw", roll, dc, dice,
            )
        roll = apply_saving_throw_minimum(state, ability, roll)
        if roll.total < dc:
            from app.combat.indomitable import use_indomitable

            reroll = use_indomitable(state, ability, dice)
            if reroll is not None:
                revision = _indomitable_revision(roll, reroll)
                roll = reroll.model_copy(update={"revisions": [*reroll.revisions, revision]})
        if roll.total < dc:
            roll, _, _ = apply_failed_save_reroll(
                state,
                roll,
                dice,
                context,
                roller=encounter_roller,
                setup=setup,
            )
        if encounter_roller is not None and setup is not None:
            adjustment = apply_resource_backed_d20_outcome_adjustment_if_useful(
                encounter_roller, setup, "saving_throw", roll, dc, dice,
            )
            if adjustment is not None:
                roll = adjustment.roll
        roll, _, _ = apply_failed_d20_test_override(
            state, roll, failed=roll.total < dc, test_kind="saving_throw",
        )
        if roll.total < dc and apply_save_success_override(state):
            return roll, True
        return roll, roll.total >= dc
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve saving throw for %s.", state.template.name)
        raise RuntimeError("Saving throw could not be resolved.") from exc
