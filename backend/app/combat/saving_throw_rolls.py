from __future__ import annotations

import logging
from typing import cast

from app.combat.ability_scores import ability_modifier_delta
from app.combat.barbarian import rage_active
from app.combat.bloodied import bloodied_saving_throw_advantage
from app.combat.condition_rules import automatically_fails_strength_dexterity_save
from app.combat.dice import DiceProvider
from app.combat.danger_sense import danger_sense_advantage
from app.combat.dodge import dodge_dex_save_advantage_sources
from app.combat.grapple import RESTRAINED_EFFECT_ID
from app.combat.modifier_stack import apply_d20_bonus_dice
from app.combat.rolls import roll_d20
from app.combat.timed_penalties import d20_disadvantage_sources
from app.domain.actions import AbilityName
from app.domain.models import CombatantState, DiceRoll, RollMode, RollRevision
from app.domain.modifiers import ModifierKind

logger = logging.getLogger(__name__)


def saving_throw_mode(
    state: CombatantState,
    ability: str,
    magical_effect: bool = False,
    advantage_sources: int = 0,
) -> RollMode:
    try:
        advantage = (
            advantage_sources
            + int(ability == "strength" and rage_active(state))
            + danger_sense_advantage(state, ability)
            + dodge_dex_save_advantage_sources(state, ability)
            + bloodied_saving_throw_advantage(state)
            + int(magical_effect and state.template.magic_resistance)
        )
        disadvantage = (
            int(ability == "dexterity" and RESTRAINED_EFFECT_ID in state.active_effect_ids)
            + d20_disadvantage_sources(state, ability)
        )
        if (advantage > 0) == (disadvantage > 0):
            return RollMode.NORMAL
        return RollMode.ADVANTAGE if advantage else RollMode.DISADVANTAGE
    except Exception as exc:
        logger.exception("Failed to resolve saving-throw mode for %s.", state.template.name)
        raise RuntimeError("Saving-throw mode could not be resolved.") from exc


def _indomitable_revision(original: DiceRoll, replacement: DiceRoll) -> RollRevision:
    try:
        return RollRevision(
            source_effect_id="indomitable", kind="full_reroll",
            original_rolls=list(original.rolls), replacement_rolls=list(replacement.rolls),
            original_modifier=original.modifier, replacement_modifier=replacement.modifier,
            original_selected=original.selected_roll, replacement_selected=replacement.selected_roll,
            original_total=original.total, replacement_total=replacement.total, accepted="replacement",
        )
    except Exception as exc:
        logger.exception("Failed to build Indomitable revision evidence.")
        raise RuntimeError("Indomitable revision could not be recorded.") from exc


def _legendary_override(state: CombatantState) -> bool:
    from app.combat.legendary_resistance import use_legendary_resistance
    return use_legendary_resistance(state)


def resolve_saving_throw(
    state: CombatantState,
    ability: str,
    dc: int,
    dice: DiceProvider,
    magical_effect: bool = False,
    advantage_sources: int = 0,
) -> tuple[DiceRoll | None, bool]:
    try:
        if ability in {"strength", "dexterity"} and automatically_fails_strength_dexterity_save(state):
            return None, _legendary_override(state)
        if ability not in state.template.saving_throw_bonuses:
            raise ValueError(f"{state.template.name} lacks a certified {ability.title()} saving throw bonus.")
        ability_name = cast(AbilityName, ability)
        save_bonus = state.template.saving_throw_bonuses[ability] + ability_modifier_delta(state, ability_name)
        roll = apply_d20_bonus_dice(
            state, ModifierKind.SAVING_THROW_BONUS_DIE,
            roll_d20(dice, save_bonus, saving_throw_mode(state, ability, magical_effect, advantage_sources)), dice,
        )
        if roll.total < dc:
            from app.combat.indomitable import use_indomitable
            reroll = use_indomitable(state, ability, dice)
            if reroll is not None:
                revision = _indomitable_revision(roll, reroll)
                roll = reroll.model_copy(update={"revisions": [*reroll.revisions, revision]})
        succeeded = roll.total >= dc
        if not succeeded:
            succeeded = _legendary_override(state)
        return roll, succeeded
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve saving throw for %s.", state.template.name)
        raise RuntimeError("Saving throw could not be resolved.") from exc
