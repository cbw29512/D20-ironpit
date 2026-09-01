from __future__ import annotations

from app.combat.defensive_spell_resolution import resolve_defensive_spell
from app.combat.friendly_buff_targeting import select_friendly_buff_targets
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.spells import DefensiveSpellAction


def _slot_resource(member: EncounterCombatant, spell: DefensiveSpellAction):
    resource_id = f"spell-slot-{spell.level}"
    resource = next((item for item in member.state.resources if item.id == resource_id), None)
    if resource is None or resource.current_uses < 1:
        return None
    return spell.level, resource


def defensive_spell_active(member: EncounterCombatant, setup: EncounterSetup, spell: DefensiveSpellAction) -> bool:
    allies = setup.heroes if member.side == "heroes" else setup.monsters
    if member.state.concentration is not None and member.state.concentration.effect_id == spell.id:
        return True
    return any(
        spell.id in target.state.active_buff_effect_ids
        or any(modifier.source_effect_id == spell.id for modifier in target.state.active_modifiers)
        for target in allies
    )


def choose_defensive_spell(member: EncounterCombatant, setup: EncounterSetup | None = None):
    if member.state.opening_buff_spell_id is not None:
        return None
    indexed = list(enumerate(member.state.template.defensive_spell_actions))
    for _, spell in sorted(indexed, key=lambda item: (-item[1].level, -item[1].priority, item[0])):
        if spell.concentration and member.state.concentration is not None:
            continue
        if setup is not None and defensive_spell_active(member, setup, spell):
            continue
        slot = _slot_resource(member, spell)
        if slot is not None:
            return spell, slot[0], slot[1]
    return None


def select_defensive_targets(
    member: EncounterCombatant,
    setup: EncounterSetup,
    spell: DefensiveSpellAction,
    slot_level: int,
) -> list[EncounterCombatant]:
    if slot_level != spell.level:
        raise ValueError("Spell upcasting is not certified; use the spell's printed slot level.")
    if spell.target_policy == "self":
        return [member]
    return select_friendly_buff_targets(member, setup, spell.range_ft, spell.target_count)


def prepare_defenses(
    setup: EncounterSetup,
    sequence: int = 1,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    members = [*setup.heroes, *setup.monsters]
    affected_states = [member.state for member in members]
    for member in members:
        choice = choose_defensive_spell(member, setup)
        if choice is None:
            continue
        spell, slot_level, resource = choice
        targets = select_defensive_targets(member, setup, spell, slot_level)
        events.append(resolve_defensive_spell(
            sequence, member, targets, spell, slot_level, resource, affected_states,
        ))
        sequence += 1
    return events, sequence
