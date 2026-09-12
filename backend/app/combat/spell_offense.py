from __future__ import annotations

from app.combat.automatic_damage_spell_policy import choose_automatic_damage_spell
from app.combat.automatic_damage_spell_resolution import resolve_automatic_damage_spell
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
    """Resolve the legal damaging spell with highest expected damage; ties conserve slots."""
    attack = choose_spell_attack(caster, setup, turn_key)
    save = choose_spell(caster, setup, turn_key)
    automatic = choose_automatic_damage_spell(caster, setup, turn_key)
    choices: list[tuple[float, int, int, str]] = []
    if attack is not None:
        choices.append((attack.expected_damage, -attack.action.level, 0, "attack"))
    if save is not None:
        choices.append((save.expected_damage, -save.slot_level, 1, "save"))
    if automatic is not None:
        choices.append((automatic.expected_damage, -automatic.slot_level, 2, "automatic"))
    if not choices:
        return [], sequence
    kind = max(choices, key=lambda item: item[:3])[3]
    if kind == "attack":
        assert attack is not None
        event = resolve_spell_attack(
            sequence, round_number, caster, attack.target, attack.action, setup, turn_key, dice,
        )
        return [event], sequence + 1
    if kind == "automatic":
        assert automatic is not None
        event = resolve_automatic_damage_spell(
            sequence, round_number, caster, automatic.target, automatic.action, setup, turn_key, dice,
        )
        return [event], sequence + 1
    assert save is not None
    return resolve_spell(sequence, round_number, caster, setup, save, turn_key, dice)
