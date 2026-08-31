from __future__ import annotations

from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType
from app.domain.spells import DefensiveSpellAction


def _slot_resource(member: EncounterCombatant, spell: DefensiveSpellAction):
    candidates = []
    for resource in member.state.resources:
        if not resource.id.startswith("spell-slot-") or resource.current_uses < 1:
            continue
        try:
            level = int(resource.id.removeprefix("spell-slot-"))
        except ValueError:
            continue
        if level >= spell.level:
            candidates.append((level, resource))
    return min(candidates, key=lambda item: item[0], default=None)


def choose_defensive_spell(member: EncounterCombatant):
    indexed = list(enumerate(member.state.template.defensive_spell_actions))
    for _, spell in sorted(indexed, key=lambda item: (-item[1].priority, item[1].level, item[0])):
        if spell.concentration:
            continue
        slot = _slot_resource(member, spell)
        if slot is not None:
            return spell, slot[0], slot[1]
    return None


def resolve_defensive_spell(
    sequence: int,
    member: EncounterCombatant,
    spell: DefensiveSpellAction,
    slot_level: int,
    resource,
) -> BattleEvent:
    if spell.concentration:
        raise ValueError("Concentration precombat spells are not certified yet.")
    if resource.current_uses < 1:
        raise ValueError(f"No level {slot_level} spell slot remains for {spell.name}.")
    resource.current_uses -= 1
    extra_levels = max(0, slot_level - spell.level)
    temporary_hp = spell.temporary_hp + extra_levels * spell.temporary_hp_per_slot_above
    granted_temp_hp = grant_temporary_hit_points(member.state, temporary_hp)
    for damage_type in spell.damage_resistances:
        typed = DamageType(damage_type)
        if typed not in member.state.temporary_damage_resistances:
            member.state.temporary_damage_resistances.append(typed)
    details = []
    if temporary_hp and granted_temp_hp:
        details.append(f"{granted_temp_hp} Temporary HP")
    if spell.damage_resistances:
        details.append("resistance to " + ", ".join(spell.damage_resistances))
    return BattleEvent(
        sequence=sequence, round_number=0, event_type="feature",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        target_id=member.combatant_id, target_name=member.state.template.name,
        feature_id=spell.id, resource_remaining=resource.current_uses,
        animation=spell.animation,
        description=(
            f"Precombat preparation: {member.state.template.name} casts {spell.name} on itself "
            f"with a level {slot_level} slot ({'; '.join(details)})."
        ),
    )


def prepare_defenses(
    setup: EncounterSetup,
    sequence: int = 1,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    for member in [*setup.heroes, *setup.monsters]:
        choice = choose_defensive_spell(member)
        if choice is None:
            continue
        spell, slot_level, resource = choice
        events.append(resolve_defensive_spell(sequence, member, spell, slot_level, resource))
        sequence += 1
    return events, sequence
