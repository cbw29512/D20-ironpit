from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.encounter_targeting import combatant_distance
from app.combat.spell_slot_selection import lowest_available_spell_slot
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.zero_hp import apply_damage
from app.domain.automatic_damage_spells import AutomaticDamageSpellAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DamageRollComponent, DiceRoll
from app.domain.weapons import DamageType


def resolve_automatic_damage_spell(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    target: EncounterCombatant,
    action: AutomaticDamageSpellAction,
    setup: EncounterSetup,
    turn_key: str,
    dice,
) -> BattleEvent:
    if action.action_cost == "reaction" or not is_available(caster.state, action.action_cost):
        raise ValueError(f"{action.name} cannot be cast in this action window.")
    if target.side == caster.side or target.state.is_dead or not target.state.is_alive:
        raise ValueError(f"{action.name} requires a living enemy target.")
    if combatant_distance(caster, target) > action.range_ft:
        raise ValueError(f"{action.name} target is out of range.")
    slot = lowest_available_spell_slot(caster.state, action.level, turn_key)
    if slot is None:
        raise ValueError(f"No legal spell slot remains for {action.name}.")
    slot_level, resource = slot
    projectile_count = action.projectile_count(slot_level)
    rolled: list[DamageRollComponent] = []
    all_rolls: list[int] = []
    damage_type = DamageType(action.damage_type)
    for index in range(projectile_count):
        rolls = [dice.roll(action.damage_dice_size) for _ in range(action.damage_dice_count_per_projectile)]
        all_rolls.extend(rolls)
        total = sum(rolls) + action.damage_bonus_per_projectile
        rolled.append(DamageRollComponent(
            source=f"{action.name} projectile {index + 1}",
            notation=f"{action.damage_dice_count_per_projectile}d{action.damage_dice_size}+{action.damage_bonus_per_projectile}",
            rolls=rolls, modifier=action.damage_bonus_per_projectile,
            damage_type=damage_type, total=total,
        ))
    hp_before = target.state.current_hp
    temporary_hp_before = target.state.temporary_hp
    death_success_before = target.state.death_save_successes
    death_failure_before = target.state.death_save_failures
    concentration_before = target.state.concentration.effect_id if target.state.concentration else None
    applied_total, components = apply_damage_defenses(target.state, rolled)
    affected = [member.state for member in [*setup.heroes, *setup.monsters]]
    apply_damage(
        target.state, applied_total, damage_types={damage_type} if applied_total else set(),
        dice=dice, affected_states=affected,
    )
    mark_slot_spell_cast(caster.state, turn_key)
    resource.current_uses -= 1
    spend(caster.state, action.action_cost)
    damage_roll = DiceRoll(
        notation=" + ".join(component.notation for component in rolled),
        rolls=all_rolls,
        modifier=projectile_count * action.damage_bonus_per_projectile,
        total=applied_total,
    )
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=caster.combatant_id, actor_name=caster.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name,
        attack_name=action.name, damage_roll=damage_roll, damage_components=components,
        hp_before=hp_before, hp_after=target.state.current_hp,
        temporary_hp_before=temporary_hp_before, temporary_hp_after=target.state.temporary_hp,
        death_save_successes_before=death_success_before, death_save_failures_before=death_failure_before,
        death_save_successes=target.state.death_save_successes, death_save_failures=target.state.death_save_failures,
        is_stable=target.state.is_stable, is_dead=target.state.is_dead,
        feature_id=action.id, resource_remaining=resource.current_uses,
        concentration_ended_effect_id=concentration_before if concentration_before and target.state.concentration is None else None,
        animation=action.animation,
        description=(f"{caster.state.template.name} casts {action.name} at slot level {slot_level}; "
                     f"{projectile_count} projectiles automatically hit {target.state.template.name}."),
    )
