from __future__ import annotations

import logging

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
    """Resolve the legal spell option with the highest expected damage; ties conserve the lower slot."""
    try:
        attack = choose_spell_attack(caster, setup, turn_key)
        save = choose_spell(caster, setup, turn_key)
        if attack is None and save is None:
            return [], sequence
        use_attack = save is None or (
            attack is not None and (
                attack.expected_damage > save.expected_damage
                or (
                    attack.expected_damage == save.expected_damage
                    and attack.slot_level <= save.slot_level
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
                slot_level=attack.slot_level,
            )
            return damage_event_chain(
                sequence + 1, round_number, caster, event, setup, dice, turn_key=turn_key,
            )
        assert save is not None
        return resolve_spell(sequence, round_number, caster, setup, save, turn_key, dice)
    except Exception:
        logger.exception("Best spell offense resolution failed for %s.", caster.combatant_id)
        raise
