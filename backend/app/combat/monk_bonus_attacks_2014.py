from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.open_hand_technique_2014 import resolve_open_hand_technique
from app.combat.pit_policy import target_order
from app.combat.stunning_strike_2014 import resolve_stunning_strike
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)
KI_RESOURCE_ID = "ki"


def _qualifying_attack_used(events: list[BattleEvent], actor_id: str) -> bool:
    return any(
        event.event_type == "attack"
        and event.actor_id == actor_id
        and event.weapon_id in {"unarmed-strike", "shortsword"}
        for event in events
    )


def _unarmed_attack(actor: EncounterCombatant):
    attacks = [actor.state.template.weapon_attack, *actor.state.template.alternate_weapon_attacks]
    return next((attack for attack in attacks if attack.weapon.id == "unarmed-strike"), None)


def _ki_resource(actor: EncounterCombatant):
    return next((item for item in actor.state.resources if item.id == KI_RESOURCE_ID), None)


def resolve_monk_bonus_attacks(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    turn_key: str,
    turn_events: list[BattleEvent],
) -> tuple[list[BattleEvent], int]:
    """Resolve 2014 Martial Arts, preferring Flurry when Ki is available."""
    try:
        state = actor.state
        features = state.template.progression_features
        if (
            state.template.ruleset != "2014"
            or not features.martial_arts_bonus_attack
            or not is_available(state, "bonus_action")
            or not _qualifying_attack_used(turn_events, actor.combatant_id)
        ):
            return [], sequence
        attack = _unarmed_attack(actor)
        if attack is None:
            raise ValueError("Certified Monk lacks an unarmed strike attack.")
        targets = [
            target for target in target_order(actor, setup)
            if combatant_distance(actor, target) <= attack.weapon.reach_ft
        ]
        if not targets:
            return [], sequence
        ki = _ki_resource(actor)
        use_flurry = bool(features.flurry_of_blows and ki is not None and ki.current_uses > 0)
        strikes = 2 if use_flurry else 1
        feature_id = "flurry-of-blows" if use_flurry else "martial-arts"
        if use_flurry:
            ki.current_uses -= 1
        spend(state, "bonus_action")
        events: list[BattleEvent] = []
        affected = [member.state for member in [*setup.heroes, *setup.monsters]]
        for _ in range(strikes):
            legal_targets = [
                target for target in target_order(actor, setup)
                if combatant_distance(actor, target) <= attack.weapon.reach_ft
            ]
            if not legal_targets or state.turn_terminated:
                break
            target = legal_targets[0]
            event = resolve_attack(
                sequence,
                round_number,
                state,
                target.state,
                attack,
                combatant_distance(actor, target),
                dice,
                actor_event_id=actor.combatant_id,
                target_event_id=target.combatant_id,
                spend_action=False,
                feature_id=feature_id,
                turn_key=turn_key,
                affected_states=affected,
            )
            events.append(event)
            sequence += 1
            if not event.hit:
                continue
            stun = resolve_stunning_strike(
                sequence,
                round_number,
                actor,
                target,
                attack,
                dice,
                affected_states=affected,
            )
            if stun is not None:
                events.append(stun)
                sequence += 1
            if use_flurry:
                technique = resolve_open_hand_technique(
                    sequence,
                    round_number,
                    actor,
                    target,
                    dice,
                )
                if technique is not None:
                    events.append(technique)
                    sequence += 1
        return events, sequence
    except Exception:
        logger.exception("Failed 2014 Monk bonus attacks for %s", actor.combatant_id)
        raise
