"""Source-typed Swallow action resolution: grappled Bite, then state transition."""
from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.attacks import resolve_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.swallow_state import swallow_after_bite
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.size import size_at_most


def resolve_swallow_action(
    sequence: int, round_number: int, attacker: EncounterCombatant,
    setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int] | None:
    """Select only source-proven Bite against an already held eligible target."""
    if not is_available(attacker.state, "action"):
        return None
    members = [*setup.heroes, *setup.monsters]
    for rule in attacker.state.template.swallow_actions:
        if len(attacker.state.swallowed_target_ids) >= rule.max_swallowed:
            continue
        attacks = ([attacker.state.template.weapon_attack]
                   if attacker.state.template.weapon_attack else [])
        attacks += attacker.state.template.alternate_weapon_attacks
        attack = next((a for a in attacks if a.id == rule.attack_id), None)
        if attack is None:
            raise ValueError("Source Swallow refers to a missing attack.")
        candidates = [
            target for target in members
            if target.side != attacker.side
            and target.state.is_alive and not target.state.is_dead
            and target.state.current_hp > 0 and target.state.swallowed is None
            and size_at_most(target.state.template.size, rule.max_target_size)
            and any(held.source_id == attacker.combatant_id for held in target.state.grapple_sources)
            and combatant_distance(attacker, target) <= attack.weapon.reach_ft
        ]
        if not candidates:
            continue
        target = min(candidates, key=lambda c: (combatant_distance(attacker, c), c.combatant_id))
        # Only this secondary action may Bite a target already held by the source.
        # Suppress the Bite's *new* grapple rider: the existing grapple ends on a
        # successful Swallow instead. Source/template are not mutated.
        swallow_bite = attack.model_copy(update={
            "forbid_target_grappled_by_self": False,
            "control_effect": None,
        })
        event = resolve_attack(
            sequence, round_number, attacker.state, target.state, swallow_bite,
            combatant_distance(attacker, target), dice,
            actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
            spend_action=True, turn_key=f"{round_number}:{attacker.combatant_id}",
            affected_states=[member.state for member in members],
            reaction_setup=setup, reaction_roller=attacker,
            feature_id="swallow",
        )
        if event.hit and swallow_after_bite(
            attacker.combatant_id, attacker.state,
            target.combatant_id, target.state, rule, bite_hit=True,
        ):
            event.description += (
                f" {target.state.template.name} is swallowed: Blinded, Restrained, "
                "total cover from outside attacks, with source-turn damage."
            )
            event.applied_condition_ids = list(dict.fromkeys(
                [*event.applied_condition_ids, "blinded", "restrained"]
            ))
        return [event], sequence + 1
    return None
