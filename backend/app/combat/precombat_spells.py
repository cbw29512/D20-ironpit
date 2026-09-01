from __future__ import annotations

from collections.abc import Iterable

from app.combat.spell_modifiers import apply_spell_modifiers
from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType, WeaponAttackKind
from app.domain.runtime import CombatantState
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect


def _slot_resource(member: EncounterCombatant, spell: DefensiveSpellAction):
    resource_id = f"spell-slot-{spell.level}"
    resource = next((item for item in member.state.resources if item.id == resource_id), None)
    if resource is None or resource.current_uses < 1:
        return None
    return spell.level, resource


def choose_defensive_spell(member: EncounterCombatant):
    indexed = list(enumerate(member.state.template.defensive_spell_actions))
    for _, spell in sorted(indexed, key=lambda item: (-item[1].priority, item[1].level, item[0])):
        slot = _slot_resource(member, spell)
        if slot is not None:
            return spell, slot[0], slot[1]
    return None


def _nearest_enemy_distance(target: EncounterCombatant, setup: EncounterSetup) -> int:
    enemies = setup.monsters if target.side == "heroes" else setup.heroes
    living = [enemy for enemy in enemies if enemy.state.is_alive and not enemy.state.is_dead]
    return min((abs(target.position_ft - enemy.position_ft) for enemy in living), default=10**9)


def _friendly_buff_priority(
    caster: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[int, int, int, str]:
    """Prefer melee line-holders, then the caster, then remaining back-line allies."""
    is_melee = target.state.template.weapon_attack.weapon.attack_kind is WeaponAttackKind.MELEE
    if target is not caster and is_melee:
        group = 0
    elif target is caster:
        group = 1
    else:
        group = 2
    return (
        group,
        _nearest_enemy_distance(target, setup),
        abs(caster.position_ft - target.position_ft),
        target.combatant_id,
    )


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
    side = setup.heroes if member.side == "heroes" else setup.monsters
    legal = [
        target for target in side
        if target.state.is_alive and not target.state.is_dead
        and abs(member.position_ft - target.position_ft) <= spell.range_ft
    ]
    legal.sort(key=lambda target: _friendly_buff_priority(member, target, setup))
    return legal[:spell.target_count]


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
    resource.current_uses -= 1
    temporary_hp = spell.temporary_hp
    for target in targets:
        grant_temporary_hit_points(target.state, temporary_hp)
        for damage_type in spell.damage_resistances:
            typed = DamageType(damage_type)
            if typed not in target.state.temporary_damage_resistances:
                target.state.temporary_damage_resistances.append(typed)
    apply_spell_modifiers(
        member.state,
        [(target.combatant_id, target.state) for target in targets],
        member.combatant_id, spell, 0, affected_states,
    )
    details = []
    if temporary_hp:
        details.append(f"{temporary_hp} Temporary HP")
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
        choice = choose_defensive_spell(member)
        if choice is None:
            continue
        spell, slot_level, resource = choice
        targets = select_defensive_targets(member, setup, spell, slot_level)
        events.append(resolve_defensive_spell(
            sequence, member, targets, spell, slot_level, resource, affected_states,
        ))
        sequence += 1
    return events, sequence
