from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.attack_legality import attack_allowed_against
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.range import resolve_attack_roll_mode
from app.combat.saving_throws import resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, SavingThrowAction, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def event_applied_damage(event: BattleEvent) -> bool:
    """Return True only when the resolved event applied positive damage."""
    return bool(event.target_id and event.damage_roll is not None and event.damage_roll.total > 0)


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _member_by_id(setup: EncounterSetup, combatant_id: str | None) -> EncounterCombatant | None:
    if combatant_id is None:
        return None
    return next((member for member in _members(setup) if member.combatant_id == combatant_id), None)


def _melee_reaction_attack(
    reactor: EncounterCombatant,
    source: EncounterCombatant,
    max_distance_ft: int,
) -> tuple[WeaponAttack, int] | None:
    distance = combatant_distance(reactor, source)
    if distance > max_distance_ft:
        return None
    attacks = [reactor.state.template.weapon_attack, *reactor.state.template.alternate_weapon_attacks]
    for attack in attacks:
        if attack.weapon.attack_kind is not WeaponAttackKind.MELEE:
            continue
        if not attack_allowed_against(attack, reactor.combatant_id, source.state):
            continue
        try:
            resolve_attack_roll_mode(attack.weapon, distance, close_enemy_active=False)
        except ValueError:
            continue
        return attack, distance
    return None


def resolve_post_damage_reactions(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    triggering_event: BattleEvent,
    setup: EncounterSetup,
    dice: DiceProvider,
    *,
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int]:
    """Resolve universal reaction attacks triggered by actual creature damage."""
    try:
        if not event_applied_damage(triggering_event):
            return [], sequence
        if triggering_event.actor_id != source.combatant_id:
            raise ValueError("Post-damage reaction source does not match the triggering event actor.")
        reactor = _member_by_id(setup, triggering_event.target_id)
        if reactor is None or reactor.combatant_id == source.combatant_id:
            return [], sequence
        feature = reactor.state.template.progression_features.damage_triggered_reaction_attack
        if feature is None or not is_available(reactor.state, "reaction"):
            return [], sequence
        if source.state.is_dead or not source.state.is_alive:
            return [], sequence
        choice = _melee_reaction_attack(reactor, source, feature.max_source_distance_ft)
        if choice is None:
            return [], sequence
        attack, distance = choice
        spend(reactor.state, "reaction")
        event = resolve_encounter_attack(
            sequence, round_number, reactor, source, attack, distance, dice, setup,
            spend_action=False, feature_id=feature.source_id, turn_key=turn_key,
            close_enemy_active=True, off_turn=True,
        )
        events = [event]
        nested, next_sequence = resolve_post_damage_reactions(
            sequence + 1, round_number, reactor, event, setup, dice, turn_key=turn_key,
        )
        events.extend(nested)
        return events, next_sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Post-damage reaction dispatch failed: source=%s target=%s.",
            source.combatant_id,
            triggering_event.target_id,
        )
        raise RuntimeError("Post-damage reaction dispatch could not be resolved.") from exc


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
    """Resolve one attack event followed immediately by any legal damage reactions."""
    event = resolve_encounter_attack(
        sequence, round_number, attacker, target, attack, distance_ft, dice, setup, **attack_options,
    )
    events = [event]
    turn_key = attack_options.get("turn_key")
    follow_ups, next_sequence = resolve_post_damage_reactions(
        sequence + 1, round_number, attacker, event, setup, dice, turn_key=turn_key,
    )
    events.extend(follow_ups)
    return events, next_sequence

def resolve_save_event_chain(
    sequence: int, round_number: int, actor: EncounterCombatant, target: EncounterCombatant,
    action: SavingThrowAction, distance_ft: int, dice: DiceProvider, setup: EncounterSetup,
    *, turn_key: str | None = None, **save_options,
) -> tuple[list[BattleEvent], int]:
    event = resolve_save_action(
        sequence, round_number, actor, target, action, distance_ft, dice, **save_options,
    )
    reactions, next_sequence = resolve_post_damage_reactions(
        sequence + 1, round_number, actor, event, setup, dice, turn_key=turn_key,
    )
    return [event, *reactions], next_sequence
