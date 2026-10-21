"""Resolve source-declared Death Triggers after actual death and before outcome."""
from __future__ import annotations

from app.combat.death_trigger_rules import consume_death_trigger
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.encounter_targeting import combatant_distance
from app.combat.save_targets import roll_shared_save_damage
from app.domain.encounters import EncounterSetup


def _declared_actions(source):
    actions = {action.id: action for action in source.state.template.death_trigger_actions}
    declared = source.state.template.death_trigger_effect_ids
    missing = [effect_id for effect_id in declared if effect_id not in actions]
    if missing:
        raise ValueError(
            f"Unbound death action on {source.state.template.id}: {', '.join(missing)}"
        )
    return [actions[effect_id] for effect_id in declared]


def resolve_pending_death_triggers(sequence, round_number, setup: EncounterSetup, dice):
    """Drain all new deaths, including chain explosions, from immutable card data."""
    events = []
    members = [*setup.heroes, *setup.monsters]
    for _ in range(len(members) + 1):
        pending = [
            member for member in members
            if member.state.is_dead
            and "death-trigger" in member.state.active_buff_effect_ids
            and not member.state.feature_use_counts.get("death-trigger", 0)
        ]
        if not pending:
            return events, sequence
        for source in pending:
            actions = _declared_actions(source)
            if not consume_death_trigger(source.state):
                continue
            for action in actions:
                targets = [
                    member for member in members
                    if member is not source
                    and member.state.is_alive
                    and not member.state.is_dead
                    and member.state.current_hp > 0
                    and combatant_distance(source, member) <= action.range_ft
                ]
                shared = roll_shared_save_damage(action, dice)
                for target in targets:
                    chain, sequence = resolve_save_event_chain(
                        sequence, round_number, source, target, action,
                        combatant_distance(source, target), dice, setup,
                        spend_action=False, check_resource=False, spend_resource=False,
                        shared_damage_rolls=shared,
                        affected_states=[member.state for member in members],
                    )
                    events.extend(chain)
    raise RuntimeError("Death Trigger cascading exceeded finite creature count.")
