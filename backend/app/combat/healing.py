from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.bloodied import is_bloodied
from app.combat.defensive_modifier_rules import healing_is_maximized
from app.combat.dice import DiceProvider
from app.combat.hit_points import effective_max_hp
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DiceRoll, HealingAction
from app.domain.traits import CombatTrait


def _distance(a: EncounterCombatant, b: EncounterCombatant) -> int:
    return abs(a.position_ft - b.position_ft)


def _slot_heal(action: HealingAction) -> bool:
    return bool(action.resource_id and action.resource_id.startswith("spell-slot-"))


def _resource_available(member: EncounterCombatant, action: HealingAction, turn_key: str | None) -> bool:
    if action.resource_id is None:
        return True
    if _slot_heal(action) and (turn_key is None or not slot_spell_available(member.state, turn_key)):
        return False
    resource = next((item for item in member.state.resources if item.id == action.resource_id), None)
    return resource is not None and resource.current_uses >= action.resource_cost


def _target_allowed(healer: EncounterCombatant, target: EncounterCombatant, action: HealingAction) -> bool:
    if target.state.is_dead or not target.state.is_alive or target.state.current_hp >= effective_max_hp(target.state):
        return False
    creature_type = str(target.state.template.creature_type or "").split(" (")[0].lower()
    excluded = {item.lower() for item in action.excluded_creature_types}
    if creature_type and creature_type in excluded:
        return False
    if CombatTrait.SWARM in target.state.template.combat_traits:
        return False
    if action.area_radius_ft is None and _distance(healer, target) > action.range_ft:
        return False
    if action.target_mode == "self":
        return target.combatant_id == healer.combatant_id
    if action.target_mode == "ally":
        return target.combatant_id != healer.combatant_id and target.side == healer.side
    if action.target_mode == "other":
        return target.combatant_id != healer.combatant_id
    return target.side == healer.side


def _self_heal_worthwhile(member: EncounterCombatant, action: HealingAction) -> bool:
    """Iron Pit policy: any proactive Action/Bonus Action heal is worthwhile once Bloodied."""
    return is_bloodied(member.state) and action.action_cost in {"action", "bonus_action"}


def choose_healing_target(
    healer: EncounterCombatant, setup: EncounterSetup, action: HealingAction, turn_key: str | None = None,
) -> EncounterCombatant | None:
    """Prefer a living 0-HP ally, then a Bloodied ally, then Bloodied self."""
    if action.action_cost == "reaction" or not is_available(healer.state, action.action_cost):
        return None
    if not _resource_available(healer, action, turn_key):
        return None
    allies = setup.heroes if healer.side == "heroes" else setup.monsters
    legal = [target for target in allies if _target_allowed(healer, target, action)]
    if action.restore_to_effective_max:
        worthwhile = [target for target in legal if target.state.current_hp == 0 or is_bloodied(target.state)]
        if not worthwhile:
            return None
        return min(
            worthwhile,
            key=lambda target: (
                target.state.current_hp / effective_max_hp(target.state),
                target.combatant_id,
            ),
        )
    others = [target for target in legal if target.combatant_id != healer.combatant_id]
    downed = [target for target in others if target.state.current_hp == 0]
    if downed:
        return max(downed, key=lambda target: target.state.death_save_failures)
    bloodied = [target for target in others if is_bloodied(target.state)]
    if bloodied:
        return min(bloodied, key=lambda target: target.state.current_hp / effective_max_hp(target.state))
    self_target = next((target for target in legal if target.combatant_id == healer.combatant_id), None)
    return self_target if self_target is not None and _self_heal_worthwhile(healer, action) else None


def _worthwhile_target_count(
    healer: EncounterCombatant, setup: EncounterSetup, action: HealingAction,
) -> int:
    allies = setup.heroes if healer.side == "heroes" else setup.monsters
    return sum(
        1 for target in allies
        if _target_allowed(healer, target, action)
        and (target.state.current_hp == 0 or is_bloodied(target.state))
    )


def _choice_priority(
    healer: EncounterCombatant, setup: EncounterSetup, action: HealingAction, target: EncounterCombatant,
) -> tuple[int, int, int, float]:
    ally = target.combatant_id != healer.combatant_id
    urgency = (
        -1
        if action.restore_to_effective_max
        else 0 if ally and target.state.current_hp == 0
        else 1 if ally
        else 2
    )
    cost = 0 if action.action_cost == "bonus_action" else 1
    useful_targets = min(action.max_targets, _worthwhile_target_count(healer, setup, action))
    group_value = -useful_targets if useful_targets >= 2 else 0
    return urgency, cost, group_value, target.state.current_hp / effective_max_hp(target.state)


def choose_healing_action(
    healer: EncounterCombatant, setup: EncounterSetup, turn_key: str | None = None,
) -> tuple[HealingAction, EncounterCombatant] | None:
    choices = [
        (action, target) for action in healer.state.template.healing_actions
        if (target := choose_healing_target(healer, setup, action, turn_key)) is not None
    ]
    return min(choices, key=lambda choice: _choice_priority(healer, setup, choice[0], choice[1])) if choices else None


def resolve_healing(
    sequence: int, round_number: int, healer: EncounterCombatant, target: EncounterCombatant,
    action: HealingAction, dice: DiceProvider, turn_key: str | None = None,
) -> BattleEvent:
    if not _target_allowed(healer, target, action) or not _resource_available(healer, action, turn_key):
        raise ValueError("Healing action is not legal for this target or turn.")
    if _slot_heal(action):
        if turn_key is None:
            raise ValueError("Spell-slot healing requires an active turn key.")
        mark_slot_spell_cast(healer.state, turn_key)
    spend(healer.state, action.action_cost)
    remaining = None
    if action.resource_id is not None:
        resource = next(item for item in healer.state.resources if item.id == action.resource_id)
        resource.current_uses -= action.resource_cost
        remaining = resource.current_uses

    feature_roll = None
    if action.percentile_success_max is not None:
        rolled = dice.roll(100)
        feature_roll = DiceRoll(
            notation="1d100",
            rolls=[rolled],
            selected_roll=rolled,
            total=rolled,
        )
        if rolled > action.percentile_success_max:
            return BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=healer.combatant_id,
                actor_name=healer.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                feature_roll=feature_roll,
                hp_before=target.state.current_hp,
                hp_after=target.state.current_hp,
                death_save_successes=target.state.death_save_successes,
                death_save_failures=target.state.death_save_failures,
                is_stable=target.state.is_stable,
                is_dead=target.state.is_dead,
                feature_id=action.id,
                resource_remaining=remaining,
                animation=action.animation,
                description=(
                    f"{healer.state.template.name} uses {action.name} and rolls {rolled} on d100; "
                    f"the intervention fails (needed {action.percentile_success_max} or lower)."
                ),
            )

    hp_before = target.state.current_hp
    if action.restore_to_effective_max:
        rolls = []
        total = effective_max_hp(target.state) - target.state.current_hp
        healed = restore_hit_points(target.state, total)
        notation = "restore-to-effective-max"
        modifier = 0
    else:
        rolls = (
            [action.dice_size for _ in range(action.dice_count)]
            if healing_is_maximized(target.state)
            else [dice.roll(action.dice_size) for _ in range(action.dice_count)]
        )
        total = sum(rolls) + action.healing_bonus
        healed = restore_hit_points(target.state, total)
        notation = (
            f"{action.dice_count}d{action.dice_size}+{action.healing_bonus}"
            if action.dice_count
            else str(action.healing_bonus)
        )
        modifier = action.healing_bonus

    description = (
        f"{healer.state.template.name} uses {action.name} on {target.state.template.name} "
        f"and restores {healed} HP."
    )
    if feature_roll is not None:
        description = (
            f"{healer.state.template.name} uses {action.name} and rolls "
            f"{feature_roll.total} on d100; the intervention succeeds. "
            f"{target.state.template.name} is restored for {healed} HP."
        )

    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="healing",
        actor_id=healer.combatant_id, actor_name=healer.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name,
        feature_roll=feature_roll,
        healing_roll=DiceRoll(notation=notation, rolls=rolls, modifier=modifier, total=healed),
        hp_before=hp_before, hp_after=target.state.current_hp,
        death_save_successes=target.state.death_save_successes, death_save_failures=target.state.death_save_failures,
        is_stable=target.state.is_stable, is_dead=target.state.is_dead,
        feature_id=action.id, resource_remaining=remaining, animation=action.animation,
        description=description,
    )
