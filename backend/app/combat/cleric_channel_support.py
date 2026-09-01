from __future__ import annotations

from app.combat.cleric_channel_divinity import resolve_channel_divinity
from app.combat.cleric_channel_policy import choose_channel_divinity
from app.combat.dice import DiceProvider
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def resolve_channel_support(
    sequence: int,
    round_number: int,
    cleric: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    choice = choose_channel_divinity(cleric, setup)
    if choice is None:
        return [], sequence
    return resolve_channel_divinity(sequence, round_number, cleric, setup, choice, dice)
