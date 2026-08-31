from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.bloodied import is_bloodied
from app.combat.dice import DiceProvider
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DiceRoll, HealingAction
from app.domain.traits import CombatTrait


def _distance(a: EncounterCombatant, b: EncounterCombatant) -> int:
    return abs(a.position_ft - b.position_ft)


def _resource_available(member: EncounterCombatant, action: HealingAction) -> bool:
    if action.resource_id is None:
        return True
    resource = next((item for item in member.state.resources if item.id == action.resource_id), None)
    return resource is not None and resource.current_uses >= action.resource_cost


def _target_allowed(healer: EncounterCombatant, target: EncounterCombatant, action: HealingAction) -> bool:
    if target.state.is_dead or not target.state.is_alive or target.state.current_hp >= target.state.template.max_hp:
        return False
    if CombatTrait.SWARM in target.state.template.combat_traits:
        return False
    if _distance(healer, target) > action.range_ft:
        return False
    if action.target_mode == "self":
        return target.combatant_id == healer.combatant_id
    if action.target_mode == "ally":
        return target.combatant_id != healer.combatant_id and target.side == healer.side
    return target.side == healer.side


def _self_heal_worthwhile(member: EncounterCombatant, action: HealingAction) -> bool:
    state = member.state
    if not is_bloodied(state):
        return False
    if action.action_cost == "bonus_action":
        return True
    if action.action_cost == "action":
        return state.current_hp * 4 <= state.template.max_hp
    return False


def choose_healing_target(
    healer: EncounterCombatant,
    setup: EncounterSetup,
    action: HealingAction,
) -> EncounterCombatant | None:
    """For one action, prefer a living 0-HP ally, then a Bloodied ally, then self."""
    if action.action_cost == "reaction" or not is_available(healer.state, action.action_cost):
        return None
    if not _resource_available(healer, action):
        return None
    allies = setup.heroes if healer.side == "heroes" else setup.monsters
    legal = [target for target in allies if _target_allowed(healer, target, action)]
    others = [target for target in legal if target.combatant_id != healer.combatant_id]
    downed = [target for target in others if target.state.current_hp == 0]
    if downed:
        return max(downed, key=lambda target: target.state.death_save_failures)
    bloodied = [target for target in others if is_bloodied(target.state)]
    if bloodied:
        return min(bloodied, key=lambda target: target.state.current_hp / target.state.template.max_hp)
    self_target = next((target for target in legal if target.combatant_id == healer.combatant_id), None)
    if self_target is not None and _self_heal_worthwhile(healer, action):
        return self_target
    return None


def _choice_priority(
    healer: EncounterCombatant,
    action: HealingAction,
    target: EncounterCombatant,
) -> tuple[int, int, float]:
    ally = target.combatant_id != healer.combatant_id
    urgency = 0 if ally and target.state.current_hp == 0 else 1 if ally else 2
    cost = 0 if action.action_cost == "bonus_action" else 1
    ratio = target.state.current_hp / target.state.template.max_hp
    return urgency, cost, ratio


def choose_healing_action(
    healer: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[HealingAction, EncounterCombatant] | None:
    choices: list[tuple[HealingAction, EncounterCombatant]] = []
    for action in healer.state.template.healing_actions:
        target = choose_healing_target(healer, setup, action)
        if target is not None:
            choices.append((action, target))
    if not choices:
        return None
    return min(choices, key=lambda choice: _choice_priority(healer, choice[0], choice[1]))


def resolve_healing(
    sequence: int,
    round_number: int,
    healer: EncounterCombatant,
    target: EncounterCombatant,
    action: HealingAction,
    dice: DiceProvider,
) -> BattleEvent:
    if not _target_allowed(healer, target, action) or not _resource_available(healer, action):
        raise ValueError("Healing action is not legal for this target.")
    spend(healer.state, action.action_cost)
    rolls = [dice.roll(action.dice_size) for _ in range(action.dice_count)]
    total = sum(rolls) + action.healing_bonus
    hp_before = target.state.current_hp
    healed = restore_hit_points(target.state, total)
    remaining = None
    if action.resource_id is not None:
        resource = next(item for item in healer.state.resources if item.id == action.resource_id)
        resource.current_uses -= action.resource_cost
        remaining = resource.current_uses
    notation = f"{action.dice_count}d{action.dice_size}+{action.healing_bonus}" if action.dice_count else str(action.healing_bonus)
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="healing",
        actor_id=healer.combatant_id, actor_name=healer.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name,
        healing_roll=DiceRoll(notation=notation, rolls=rolls, modifier=action.healing_bonus, total=total),
        hp_before=hp_before, hp_after=target.state.current_hp,
        death_save_successes=target.state.death_save_successes,
        death_save_failures=target.state.death_save_failures,
        is_stable=target.state.is_stable, is_dead=target.state.is_dead,
        feature_id=action.id, resource_remaining=remaining, animation=action.animation,
        description=f"{healer.state.template.name} uses {action.name} on {target.state.template.name} and restores {healed} HP.",
    )
