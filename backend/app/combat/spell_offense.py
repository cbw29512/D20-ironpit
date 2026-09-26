from __future__ import annotations

import logging

from app.combat.concentration_repeat_saves import (
    choose_concentration_repeat_save,
    resolve_concentration_repeat_save,
)
from app.combat.damage_reaction_events import damage_event_chain
from app.combat.spell_attack_policy import choose_spell_attack
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.spell_policy import choose_spell
from app.combat.spell_resolution import resolve_spell
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def resolve_best_spell_offense(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve the best legal spell offense; free ongoing spell Actions win equal-damage ties."""
    try:
        repeat = choose_concentration_repeat_save(caster, setup)
        attack = choose_spell_attack(caster, setup, turn_key)
        save = choose_spell(caster, setup, turn_key)

        normal_expected = max(
            attack.expected_damage if attack is not None else float("-inf"),
            save.expected_damage if save is not None else float("-inf"),
        )
        if repeat is not None and repeat.expected_damage >= normal_expected:
            return resolve_concentration_repeat_save(
                sequence,
                round_number,
                caster,
                setup,
                repeat,
                turn_key,
                dice,
            )

        if attack is None and save is None:
            return [], sequence
        use_attack = save is None or (
            attack is not None and (
                attack.expected_damage > save.expected_damage
                or (
                    attack.expected_damage == save.expected_damage
                    and attack.action.level <= save.action.level
                )
            )
        )
        if use_attack:
            assert attack is not None
            event = resolve_spell_attack(
                sequence,
                round_number,
                caster,
                attack.target,
                attack.action,
                setup,
                turn_key,
                dice,
            )
            return damage_event_chain(
                sequence + 1,
                round_number,
                caster,
                event,
                setup,
                dice,
                turn_key=turn_key,
            )
        assert save is not None
        return resolve_spell(sequence, round_number, caster, setup, save, turn_key, dice)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Spell-offense resolution failed for %s.", caster.combatant_id)
        raise RuntimeError("Spell offense could not be resolved.") from exc
