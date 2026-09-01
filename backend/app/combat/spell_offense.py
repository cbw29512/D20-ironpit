from __future__ import annotations

from app.combat.spell_attack_policy import choose_spell_attack
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.spell_policy import choose_spell
from app.combat.spell_resolution import resolve_spell
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def resolve_best_spell_offense(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Resolve the legal spell option with the highest expected damage; ties conserve the lower slot."""
    attack = choose_spell_attack(caster, setup, turn_key)
    save = choose_spell(caster, setup, turn_key)
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
            sequence, round_number, caster, attack.target, attack.action, setup, turn_key, dice,
        )
        return [event], sequence + 1
    assert save is not None
    return resolve_spell(sequence, round_number, caster, setup, save, turn_key, dice)
