from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available, spend
from app.combat.damage_defenses import adjusted_damage_amount, apply_damage_defenses
from app.combat.encounter_targeting import combatant_distance
from app.combat.resources import action_resource_available, resolved_resource_id, spend_action_resource
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available, spell_action_resource_available
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll
from app.domain.spells import AutomaticSpellAction


@dataclass(frozen=True)
class AutomaticSpellChoice:
    action: AutomaticSpellAction
    slot_level: int
    target_ids: tuple[str, ...]
    expected_damage: float


def _application_damage(action: AutomaticSpellAction) -> float:
    return action.damage_dice_count * (action.damage_dice_size + 1) / 2 + action.damage_bonus


def choose_automatic_spell(caster: EncounterCombatant, setup: EncounterSetup, turn_key: str) -> AutomaticSpellChoice | None:
    enemies = setup.monsters if caster.side == "heroes" else setup.heroes
    candidates: list[AutomaticSpellChoice] = []
    for action in caster.state.template.automatic_spell_actions:
        if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
            continue
        if not spell_action_resource_available(
            caster.state,
            level=action.level,
            resource_id=action.resource_id,
            resource_cost=action.resource_cost,
            turn_key=turn_key,
        ):
            continue
        legal = [target for target in enemies if target.state.is_alive and not target.state.is_dead
                 and target.state.current_hp > 0 and combatant_distance(caster, target) <= action.range_ft]
        if not legal:
            continue
        raw = _application_damage(action)
        scored = sorted(
            ((adjusted_damage_amount(round(raw), DamageType(action.damage_type), target.state), target) for target in legal),
            key=lambda item: (item[0], -item[1].state.current_hp, item[1].combatant_id), reverse=True,
        )
        if not scored:
            continue
        if not action.allow_split_targets:
            target_ids = (scored[0][1].combatant_id,) * action.applications
        else:
            projected = {target.combatant_id: target.state.current_hp for _, target in scored}
            target_ids_list: list[str] = []
            for _ in range(action.applications):
                damage, target = max(
                    scored,
                    key=lambda item: (min(item[0], projected[item[1].combatant_id]), item[0], item[1].combatant_id),
                )
                target_ids_list.append(target.combatant_id)
                projected[target.combatant_id] = max(0, projected[target.combatant_id] - damage)
            target_ids = tuple(target_ids_list)
        expected = sum(adjusted_damage_amount(round(raw), DamageType(action.damage_type),
                                              next(target.state for target in legal if target.combatant_id == target_id))
                       for target_id in target_ids)
        candidates.append(AutomaticSpellChoice(action, action.level, target_ids, expected))
    return max(candidates, key=lambda choice: (choice.expected_damage, -choice.action.level, choice.action.id)) if candidates else None


def resolve_automatic_spell(sequence: int, round_number: int, caster: EncounterCombatant, setup: EncounterSetup,
                            choice: AutomaticSpellChoice, turn_key: str, dice) -> tuple[list[BattleEvent], int]:
    action = choice.action
    if not is_available(caster.state, action.action_cost):
        raise ValueError(f"{action.action_cost} is unavailable for {action.name}.")
    fallback_id = f"spell-slot-{choice.slot_level}"
    resource_id = resolved_resource_id(action.resource_id, fallback_id)
    uses_spell_slot = bool(resource_id and resource_id.startswith("spell-slot-"))
    if uses_spell_slot and not slot_spell_available(caster.state, turn_key):
        raise ValueError(f"A leveled spell was already cast this turn before {action.name}.")
    if not action_resource_available(caster.state, action.resource_id, action.resource_cost, fallback_resource_id=fallback_id):
        raise ValueError(f"Resource {resource_id!r} is unavailable for {action.name}.")
    members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    if len(choice.target_ids) != action.applications:
        raise ValueError(f"{action.name} requires exactly {action.applications} automatic applications.")
    for target_id in choice.target_ids:
        target = members.get(target_id)
        if (
            target is None
            or target.side == caster.side
            or not target.state.is_alive
            or target.state.is_dead
            or target.state.current_hp <= 0
            or combatant_distance(caster, target) > action.range_ft
        ):
            raise ValueError(f"Illegal automatic spell target {target_id!r} for {action.name}.")

    remaining = spend_action_resource(caster.state, action.resource_id, action.resource_cost, fallback_resource_id=fallback_id)
    if uses_spell_slot:
        mark_slot_spell_cast(caster.state, turn_key)
    spend(caster.state, action.action_cost)
    events = [BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature", actor_id=caster.combatant_id,
        actor_name=caster.state.template.name, feature_id=action.id, resource_remaining=remaining,
        animation=action.animation,
        description=f"{caster.state.template.name} casts {action.name}; {action.applications} automatic applications resolve.",
    )]
    sequence += 1
    affected_states = [member.state for member in members.values()]
    for application, target_id in enumerate(choice.target_ids, start=1):
        target = members[target_id]
        rolls = [dice.roll(action.damage_dice_size) for _ in range(action.damage_dice_count)]
        total = max(0, sum(rolls) + action.damage_bonus)
        component = DamageRollComponent(
            source=f"{action.name} application {application}",
            notation=f"{action.damage_dice_count}d{action.damage_dice_size}+{action.damage_bonus}",
            rolls=rolls, modifier=action.damage_bonus, damage_type=DamageType(action.damage_type), total=total,
        )
        applied, components = apply_damage_defenses(target.state, [component])
        before = target.state.current_hp
        if applied:
            apply_damage(target.state, applied, damage_types={DamageType(action.damage_type)}, dice=dice,
                         affected_states=affected_states)
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature", actor_id=caster.combatant_id,
            actor_name=caster.state.template.name, target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=action.id, damage_roll=DiceRoll(
                notation=component.notation, rolls=rolls, modifier=action.damage_bonus, total=applied,
            ), damage_components=components, hp_before=before, hp_after=target.state.current_hp,
            animation=action.animation,
            description=f"{action.name} application {application} deals {applied} {action.damage_type} damage to {target.state.template.name}.",
        ))
        sequence += 1
    return events, sequence
