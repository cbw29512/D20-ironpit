from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.bloodied import is_bloodied
from app.combat.defensive_modifier_rules import healing_is_maximized
from app.combat.hit_points import effective_max_hp
from app.combat.spellcasting import slot_spell_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import HealingAction
from app.domain.traits import CombatTrait


def slot_heal(action: HealingAction) -> bool:
    return bool(action.resource_id and action.resource_id.startswith("spell-slot-"))


def healing_dice_maximized(
    healer: EncounterCombatant,
    target: EncounterCombatant,
) -> bool:
    """Combine caster-owned and recipient-owned healing maximization semantics."""
    return (
        healer.state.template.progression_features.outgoing_healing_dice_maximizer is not None
        or healing_is_maximized(target.state)
    )


def resource_available(
    member: EncounterCombatant,
    action: HealingAction,
    turn_key: str | None,
) -> bool:
    if action.resource_id is None:
        return True
    if slot_heal(action) and (turn_key is None or not slot_spell_available(member.state, turn_key)):
        return False
    resource = next((item for item in member.state.resources if item.id == action.resource_id), None)
    return resource is not None and resource.current_uses >= action.resource_cost


def target_allowed(
    healer: EncounterCombatant,
    target: EncounterCombatant,
    action: HealingAction,
) -> bool:
    if target.state.is_dead or not target.state.is_alive:
        return False
    if target.state.current_hp >= effective_max_hp(target.state):
        return False
    creature_type = str(target.state.template.creature_type or "").split(" (")[0].lower()
    excluded = {item.lower() for item in action.excluded_creature_types}
    if creature_type and creature_type in excluded:
        return False
    if CombatTrait.SWARM in target.state.template.combat_traits:
        return False
    if action.area_radius_ft is None and abs(healer.position_ft - target.position_ft) > action.range_ft:
        return False
    if action.target_mode == "self":
        return target.combatant_id == healer.combatant_id
    if action.target_mode == "ally":
        return target.combatant_id != healer.combatant_id and target.side == healer.side
    if action.target_mode == "other":
        return target.combatant_id != healer.combatant_id
    return target.side == healer.side


def choose_healing_target(
    healer: EncounterCombatant,
    setup: EncounterSetup,
    action: HealingAction,
    turn_key: str | None = None,
) -> EncounterCombatant | None:
    if action.action_cost == "reaction" or not is_available(healer.state, action.action_cost):
        return None
    if not resource_available(healer, action, turn_key):
        return None
    allies = setup.heroes if healer.side == "heroes" else setup.monsters
    legal = [target for target in allies if target_allowed(healer, target, action)]
    if action.restore_to_effective_max:
        worthwhile = [target for target in legal if target.state.current_hp == 0 or is_bloodied(target.state)]
        return min(
            worthwhile,
            key=lambda target: (
                target.state.current_hp / effective_max_hp(target.state),
                target.combatant_id,
            ),
        ) if worthwhile else None
    others = [target for target in legal if target.combatant_id != healer.combatant_id]
    downed = [target for target in others if target.state.current_hp == 0]
    if downed:
        return max(downed, key=lambda target: target.state.death_save_failures)
    bloodied = [target for target in others if is_bloodied(target.state)]
    if bloodied:
        return min(bloodied, key=lambda target: target.state.current_hp / effective_max_hp(target.state))
    self_target = next((target for target in legal if target.combatant_id == healer.combatant_id), None)
    return (
        self_target
        if self_target is not None
        and is_bloodied(healer.state)
        and action.action_cost in {"action", "bonus_action"}
        else None
    )


def _worthwhile_target_count(
    healer: EncounterCombatant,
    setup: EncounterSetup,
    action: HealingAction,
) -> int:
    allies = setup.heroes if healer.side == "heroes" else setup.monsters
    return sum(
        1 for target in allies
        if target_allowed(healer, target, action)
        and (target.state.current_hp == 0 or is_bloodied(target.state))
    )


def _priority(
    healer: EncounterCombatant,
    setup: EncounterSetup,
    action: HealingAction,
    target: EncounterCombatant,
) -> tuple[int, int, int, float]:
    ally = target.combatant_id != healer.combatant_id
    urgency = (
        -1 if action.restore_to_effective_max
        else 0 if ally and target.state.current_hp == 0
        else 1 if ally else 2
    )
    cost = 0 if action.action_cost == "bonus_action" else 1
    useful = min(action.max_targets, _worthwhile_target_count(healer, setup, action))
    return urgency, cost, (-useful if useful >= 2 else 0), target.state.current_hp / effective_max_hp(target.state)


def choose_healing_action(
    healer: EncounterCombatant,
    setup: EncounterSetup,
    turn_key: str | None = None,
) -> tuple[HealingAction, EncounterCombatant] | None:
    choices = [
        (action, target)
        for action in healer.state.template.healing_actions
        if (target := choose_healing_target(healer, setup, action, turn_key)) is not None
    ]
    return min(choices, key=lambda choice: _priority(healer, setup, choice[0], choice[1])) if choices else None
