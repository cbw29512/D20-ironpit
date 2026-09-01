from __future__ import annotations

from collections.abc import Iterable

from app.combat.friendly_buff_targeting import select_friendly_buff_targets
from app.combat.spell_modifiers import apply_spell_modifiers
from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType
from app.domain.runtime import CombatantState
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect


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
    indexed = list(enumerate(member.state.template.defensive_spell_actions))
    for _, spell in sorted(indexed, key=lambda item: (-item[1].priority, item[1].level, item[0])):
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


def _modifier_detail(effect: SpellModifierEffect) -> str:
    if effect.kind == "armor-class":
        return f"{effect.flat_bonus:+d} AC"
    if effect.kind == "speed":
        return f"{effect.flat_bonus:+d} Speed"
    if effect.dice_count:
        return f"{effect.dice_count}d{effect.dice_size} {effect.kind}"
    return effect.kind


def resolve_defensive_spell(
    sequence: int,
    member: EncounterCombatant,
    targets: list[EncounterCombatant],
    spell: DefensiveSpellAction,
    slot_level: int,
    resource,
    affected_states: Iterable[CombatantState] | None = None,
) -> BattleEvent:
    if slot_level != spell.level:
        raise ValueError("Spell upcasting is not certified; use the spell's printed slot level.")
    if resource.current_uses < 1:
        raise ValueError(f"No level {slot_level} spell slot remains for {spell.name}.")
    if not targets:
        raise ValueError(f"{spell.name} has no legal precombat targets.")
    if spell.concentration and member.state.concentration is not None:
        raise ValueError(f"{member.state.template.name} is already concentrating and will not replace the active buff automatically.")
    if any(
        spell.id in target.state.active_buff_effect_ids
        or any(modifier.source_effect_id == spell.id for modifier in target.state.active_modifiers)
        for target in targets
    ):
        raise ValueError(f"{spell.name} is already active on a selected target.")
    resource.current_uses -= 1
    temp_hp_details: list[str] = []
    for target in targets:
        before = target.state.temporary_hp
        after = grant_temporary_hit_points(target.state, spell.temporary_hp)
        if after > before:
            temp_hp_details.append(f"{target.state.template.name} {after} Temporary HP")
        if spell.max_hp_increase:
            target.state.max_hp_bonus += spell.max_hp_increase
        if spell.current_hp_increase:
            target.state.current_hp += spell.current_hp_increase
        for damage_type in spell.damage_resistances:
            typed = DamageType(damage_type)
            if typed not in target.state.temporary_damage_resistances:
                target.state.temporary_damage_resistances.append(typed)
        if not spell.concentration and spell.id not in target.state.active_buff_effect_ids:
            target.state.active_buff_effect_ids.append(spell.id)
    apply_spell_modifiers(
        member.state,
        [(target.combatant_id, target.state) for target in targets],
        member.combatant_id, spell, 0, affected_states,
    )
    details = [*temp_hp_details]
    if spell.max_hp_increase:
        details.append(f"+{spell.max_hp_increase} Hit Point maximum")
    if spell.current_hp_increase:
        details.append(f"+{spell.current_hp_increase} current Hit Points")
    if spell.damage_resistances:
        details.append("resistance to " + ", ".join(spell.damage_resistances))
    details.extend(_modifier_detail(effect) for effect in spell.modifier_effects)
    if spell.concentration:
        details.append("Concentration")
    names = ", ".join(target.state.template.name for target in targets)
    single = targets[0] if len(targets) == 1 else None
    return BattleEvent(
        sequence=sequence, round_number=0, event_type="feature",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        target_id=single.combatant_id if single else None,
        target_name=single.state.template.name if single else None,
        feature_id=spell.id, resource_remaining=resource.current_uses,
        animation=spell.animation,
        description=(
            f"Precombat preparation: {member.state.template.name} casts {spell.name} with a level {slot_level} slot "
            f"on {names} ({'; '.join(details)})."
        ),
    )


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
