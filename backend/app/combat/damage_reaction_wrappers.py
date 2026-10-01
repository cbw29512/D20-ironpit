from __future__ import annotations

import logging

from app.combat.damage_reaction_events import damage_event_chain
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.resource_backed_on_hit_save import resolve_resource_backed_on_hit_save
from app.combat.saving_throws import resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction, WeaponAttack

logger = logging.getLogger(__name__)


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
    try:
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
        next_sequence = sequence + 1
        prefix = [event]
        if event.hit:
            actual_target = next(
                (
                    member
                    for member in [*setup.heroes, *setup.monsters]
                    if member.combatant_id == event.target_id
                ),
                target,
            )
            rider = resolve_resource_backed_on_hit_save(
                next_sequence,
                round_number,
                attacker,
                actual_target,
                attack,
                dice,
                attack_options.get("turn_key") or f"{round_number}:{attacker.combatant_id}",
                affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
            )
            if rider is not None:
                prefix.append(rider.event)
                next_sequence += 1
        reactions, final_sequence = damage_event_chain(
            next_sequence,
            round_number,
            attacker,
            event,
            setup,
            dice,
            turn_key=attack_options.get("turn_key"),
        )
        return [*prefix, *reactions[1:]], final_sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Attack event-chain resolution failed: attacker=%s target=%s attack=%s sequence=%s.",
            attacker.combatant_id,
            target.combatant_id,
            attack.id,
            sequence,
        )
        raise RuntimeError("Attack event chain could not be resolved.") from exc


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
    try:
        event = resolve_save_action(
            sequence,
            round_number,
            actor,
            target,
            action,
            distance_ft,
            dice,
            setup=setup,
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
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Save event-chain resolution failed: actor=%s target=%s action=%s sequence=%s.",
            actor.combatant_id,
            target.combatant_id,
            action.id,
            sequence,
        )
        raise RuntimeError("Save event chain could not be resolved.") from exc
