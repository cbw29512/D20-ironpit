from __future__ import annotations

from app.combat.damage_reaction_events import damage_event_chain
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.saving_throws import resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction, WeaponAttack


def resolve_attack_event_chain(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    distance_ft: int,
    dice: DiceProvider,
    setup: EncounterSetup,
    **attack_options,
) -> tuple[list[BattleEvent], int]:
    """Resolve one attack and any immediate post-damage reaction chain."""
    event = resolve_encounter_attack(
        sequence,
        round_number,
        attacker,
        target,
        attack,
        distance_ft,
        dice,
        setup,
        **attack_options,
    )
    return damage_event_chain(
        sequence + 1,
        round_number,
        attacker,
        event,
        setup,
        dice,
        turn_key=attack_options.get("turn_key"),
    )


def resolve_save_event_chain(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    target: EncounterCombatant,
    action: SavingThrowAction,
    distance_ft: int,
    dice: DiceProvider,
    setup: EncounterSetup,
    *,
    turn_key: str | None = None,
    **save_options,
) -> tuple[list[BattleEvent], int]:
    """Resolve one save action and any immediate post-damage reaction chain."""
    event = resolve_save_action(
        sequence,
        round_number,
        actor,
        target,
        action,
        distance_ft,
        dice,
        **save_options,
    )
    return damage_event_chain(
        sequence + 1,
        round_number,
        actor,
        event,
        setup,
        dice,
        turn_key=turn_key,
    )
