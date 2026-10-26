from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.automatic_save_failures import automatically_fails_save
from app.combat.defensive_modifier_rules import saving_throw_advantage_source_names
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.target_chosen_save import choose_save_ability
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DiceRoll, SavingThrowAction
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SaveAttemptResult:
    action: SavingThrowAction
    selected_ability: str
    automatic_failure: bool
    advantage_sources: tuple[str, ...]
    save_roll: DiceRoll | None
    succeeded: bool


def resolve_save_attempt(
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    dice: DiceProvider,
    round_number: int,
    *,
    spell_effect: bool = False,
    save_disadvantage_sources: tuple[str, ...] = (),
    save_advantage_sources: tuple[str, ...] = (),
    setup: EncounterSetup | None = None,
) -> SaveAttemptResult:
    try:
        source_type = (
            str(actor.state.template.creature_type)
            .split(" (")[0]
            .strip()
            .casefold()
            if actor.state.template.creature_type
            else None
        )
        effect_tags = {
            str(tag).strip().casefold()
            for tag in action.effect_tags
            if str(tag).strip()
        }
        if str(action.damage_type or "").casefold() == "poison":
            effect_tags.add("poison")
        context = SavingThrowContext(
            magical_effect=action.magical_effect,
            spell_effect=spell_effect,
            source_creature_type=source_type,
            effect_tags=frozenset(effect_tags),
            disadvantage_sources=save_disadvantage_sources,
            advantage_sources=save_advantage_sources,
        )
        selected = (
            choose_save_ability(
                target.state,
                action.save_ability_choices,
                action.dc,
                context,
                member=target,
                setup=setup,
            )
            if action.save_ability_choices
            else action.save_ability
        )
        active_action = (
            action.model_copy(update={"save_ability": selected})
            if selected != action.save_ability
            else action
        )
        automatic = automatically_fails_save(active_action, target)
        advantages = (
            ()
            if automatic
            else saving_throw_advantage_source_names(
                target.state, selected, context
            )
        )
        if automatic:
            save_roll, succeeded = None, False
        else:
            save_roll, succeeded = resolve_saving_throw(
                target.state,
                selected,
                action.dc,
                dice,
                context,
                round_number=round_number,
                encounter_roller=target,
                setup=setup,
            )
        return SaveAttemptResult(
            action=active_action,
            selected_ability=selected,
            automatic_failure=automatic,
            advantage_sources=advantages,
            save_roll=save_roll,
            succeeded=succeeded,
        )
    except Exception:
        logger.exception(
            "Failed to resolve saving-throw attempt for %s against %s.",
            action.id,
            target.combatant_id,
        )
        raise
