from __future__ import annotations

import logging

from app.combat.barbarian import rage_active
from app.combat.condition_rules import automatically_fails_strength_dexterity_save
from app.combat.danger_sense import danger_sense_advantage
from app.combat.dice import DiceProvider
from app.combat.dodge import dodge_dex_save_advantage_sources
from app.combat.grapple import RESTRAINED_EFFECT_ID
from app.combat.modifier_stack import apply_d20_bonus_dice
from app.combat.rolls import roll_d20
from app.domain.models import CombatantState, DiceRoll, RollMode, RollRevision
from app.domain.modifiers import ModifierKind
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def saving_throw_mode(state: CombatantState, ability: str, *, magical_effect: bool = False) -> RollMode:
    try:
        advantage = (
            int(ability == "strength" and rage_active(state))
            + danger_sense_advantage(state, ability)
            + dodge_dex_save_advantage_sources(state, ability)
            + int(magical_effect and CombatTrait.MAGIC_RESISTANCE in state.template.combat_traits)
        )
        disadvantage = 1 if ability == "dexterity" and RESTRAINED_EFFECT_ID in state.active_effect_ids else 0
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
    *,
    magical_effect: bool = False,
) -> tuple[DiceRoll | None, bool]:
    try:
        if ability in {"strength", "dexterity"} and automatically_fails_strength_dexterity_save(state):
            return None, False
        if ability not in state.template.saving_throw_bonuses:
            raise ValueError(f"{state.template.name} lacks a certified {ability.title()} saving throw bonus.")
        roll = apply_d20_bonus_dice(
            state,
            ModifierKind.SAVING_THROW_BONUS_DIE,
            roll_d20(
                dice,
                state.template.saving_throw_bonuses[ability],
                saving_throw_mode(state, ability, magical_effect=magical_effect),
            ),
            dice,
        )
        if roll.total < dc:
            from app.combat.indomitable import use_indomitable

            reroll = use_indomitable(state, ability, dice)
            if reroll is not None:
                revision = _indomitable_revision(roll, reroll)
                roll = reroll.model_copy(update={"revisions": [*reroll.revisions, revision]})
        return roll, roll.total >= dc
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve saving throw for %s.", state.template.name)
        raise RuntimeError("Saving throw could not be resolved.") from exc
