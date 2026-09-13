from __future__ import annotations

from app.combat.automatic_spell import choose_automatic_spell, resolve_automatic_spell
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
    automatic = choose_automatic_spell(caster, setup, turn_key)
    candidates = [
        (choice.expected_damage, -choice.action.level, kind, choice)
        for kind, choice in (("attack", attack), ("save", save), ("automatic", automatic))
        if choice is not None
    ]
    if not candidates:
        return [], sequence
    _, _, kind, choice = max(candidates, key=lambda item: (item[0], item[1], item[2]))
    if kind == "attack":
        event = resolve_spell_attack(
            sequence, round_number, caster, choice.target, choice.action, setup, turn_key, dice,
        )
        return [event], sequence + 1
    if kind == "automatic":
        return resolve_automatic_spell(sequence, round_number, caster, setup, choice, turn_key, dice)
    return resolve_spell(sequence, round_number, caster, setup, choice, turn_key, dice)
