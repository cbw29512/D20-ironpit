from __future__ import annotations

import logging

from app.combat.concentration import end_concentration
from app.combat.dice import roll_dice
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def start_of_turn_timed_burns(
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> list[tuple[str, int, str]]:
    """Apply printed start-of-turn burn dice, then end the effect on a successful save."""
    try:
        packets: list[tuple[str, int, str]] = []
        affected = [item.state for item in [*setup.heroes, *setup.monsters]]
        for effect in list(member.state.timed_effects):
            if effect.start_of_turn_dice_count <= 0 or effect.start_of_turn_damage_type is None:
                continue
            total = roll_dice(dice, effect.start_of_turn_dice_count, effect.start_of_turn_dice_size)
            packets.append((
                effect.source_effect_id or effect.effect_id,
                total,
                str(effect.start_of_turn_damage_type),
            ))
            if not (
                effect.start_of_turn_save_ends
                and effect.start_of_turn_save_ability
                and effect.start_of_turn_save_dc
            ):
                continue
            _, succeeded = resolve_saving_throw(
                member.state,
                effect.start_of_turn_save_ability,
                effect.start_of_turn_save_dc,
                dice,
                SavingThrowContext(effect_tags=frozenset({"spell"})),
                encounter_roller=member,
                setup=setup,
            )
            if not succeeded:
                continue
            remove_effect_instance(member.state, effect)
            for source in [*setup.heroes, *setup.monsters]:
                concentration = source.state.concentration
                if concentration is None:
                    continue
                if (
                    concentration.source_id == effect.source_id
                    and concentration.effect_id == effect.source_effect_id
                ):
                    end_concentration(source.state, affected)
        return packets
    except Exception:
        logger.exception("Start-of-turn timed burn failed for %s.", member.combatant_id)
        raise
