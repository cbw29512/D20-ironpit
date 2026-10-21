"""Source-driven death effects, dispatched after actual death, never at hero 0 HP."""
from __future__ import annotations

from functools import lru_cache

from app.combat.death_trigger_rules import consume_death_trigger
from app.combat.damage_reaction_wrappers import resolve_save_event_chain
from app.combat.encounter_targeting import combatant_distance
from app.combat.save_targets import roll_shared_save_damage
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterSetup
from app.domain.models import SavingThrowAction


@lru_cache(maxsize=1)
def _source_death_actions():
    return {
        "2014-" + card.id: {
            action["id"]: action
            for action in card.death_trigger_actions
            if isinstance(action, dict) and action.get("id")
        }
        for card in load_monster_source_2014()
        if card.death_trigger_actions
    }


def _compile_death_save_action(raw):
    # Fail closed on unknown shapes; source text must not be guessed.
    area = raw.get("area")
    if area != {"shape": "emanation", "origin": "self", "radius_ft": raw["range_ft"]}:
        raise ValueError(f"Unsupported death trigger geometry: {raw!r}")
    return SavingThrowAction.model_validate({
        "id": raw["id"], "name": raw["name"], "save_ability": raw["save_ability"],
        "dc": raw["dc"], "range_ft": raw["range_ft"],
        "damage_dice_count": raw["damage_dice_count"],
        "damage_dice_size": raw["damage_dice_size"],
        "damage_bonus": raw["damage_bonus"], "damage_type": raw["damage_type"],
        "success_damage": raw["success_damage"],
        "target_scope": "all-other-creatures", "animation": raw.get("animation", "death-trigger"),
    })


def resolve_pending_death_triggers(sequence, round_number, setup: EncounterSetup, dice):
    """Drain all new deaths, including chain explosions, using immutable source parameters."""
    events = []
    members = [*setup.heroes, *setup.monsters]
    # Bound by once-only consumption per combatant, even for cascading bursts.
    for _ in range(len(members) + 1):
        pending = [member for member in members
                   if member.state.is_dead
                   and "death-trigger" in member.state.active_buff_effect_ids
                   and not member.state.feature_use_counts.get("death-trigger", 0)]
        if not pending:
            return events, sequence
        for source in pending:
            effects = _source_death_actions().get(source.state.template.id, {})
            declared = source.state.template.death_trigger_effect_ids
            if any(effect_id not in effects for effect_id in declared):
                raise ValueError(f"Unbound death action on {source.state.template.id}")
            actions = [_compile_death_save_action(effects[key]) for key in declared]
            if not consume_death_trigger(source.state):
                continue
            for action in actions:
                targets = [member for member in members if member is not source
                           and member.state.is_alive and not member.state.is_dead
                           and member.state.current_hp > 0
                           and combatant_distance(source, member) <= action.range_ft]
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
    raise RuntimeError("Death trigger cascading exceeded finite creature count.")
