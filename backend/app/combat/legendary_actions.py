from __future__ import annotations

from app.combat.area_save_actions import resolve_area_save_action
from app.combat.area_save_targeting import legal_area_save_placements
from app.combat.attacks import resolve_attack
from app.combat.condition_rules import is_incapacitated
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.range import resolve_attack_roll_mode
from app.combat.resources import resource_available, resource_state, spend_resource
from app.combat.saving_throws import legal_save_action, resolve_save_action
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.event_support import DiceRoll, RollMode
from app.domain.events import BattleEvent
from app.domain.legendary_actions import LegendaryActionOption
from app.domain.runtime import CombatantState

LEGENDARY_ACTION_RESOURCE_ID = "legendary-actions"


def refresh_legendary_actions(state: CombatantState) -> None:
    """2014 legendary action uses return to full at the start of the owner's turn."""
    resource = resource_state(state, LEGENDARY_ACTION_RESOURCE_ID)
    if resource is not None:
        resource.current_uses = resource.max_uses


def _attack_by_id(owner: EncounterCombatant, attack_id: str):
    attacks = [owner.state.template.weapon_attack, *owner.state.template.alternate_weapon_attacks]
    return next((attack for attack in attacks if attack.id == attack_id), None)


def _attack_target(
    owner: EncounterCombatant,
    setup: EncounterSetup,
    option: LegendaryActionOption,
) -> tuple[EncounterCombatant, object, int] | None:
    if option.attack_id is None:
        return None
    attack = _attack_by_id(owner, option.attack_id)
    if attack is None:
        return None
    candidates: list[tuple[int, str, EncounterCombatant]] = []
    for target in living_opponents(owner, setup):
        distance = combatant_distance(owner, target)
        try:
            resolve_attack_roll_mode(attack.weapon, distance, close_enemy_active=False)
        except ValueError:
            continue
        candidates.append((distance, target.combatant_id, target))
    if not candidates:
        return None
    distance, _, target = min(candidates, key=lambda item: (item[0], item[1]))
    return target, attack, distance


def _single_save_target(
    owner: EncounterCombatant,
    setup: EncounterSetup,
    option: LegendaryActionOption,
) -> tuple[EncounterCombatant, int] | None:
    action = option.save_action
    if action is None or action.area is not None:
        return None
    candidates: list[tuple[int, str, EncounterCombatant]] = []
    for target in living_opponents(owner, setup):
        distance = combatant_distance(owner, target)
        if legal_save_action(action, target, distance):
            candidates.append((distance, target.combatant_id, target))
    if not candidates:
        return None
    distance, _, target = min(candidates, key=lambda item: (item[0], item[1]))
    return target, distance


def _priority(
    owner: EncounterCombatant,
    setup: EncounterSetup,
    option: LegendaryActionOption,
) -> tuple[int, int, str] | None:
    if not resource_available(owner.state, LEGENDARY_ACTION_RESOURCE_ID, option.cost):
        return None
    if option.kind == "save" and option.save_action is not None and option.save_action.area is not None:
        placements = legal_area_save_placements(owner, setup, option.save_action)
        if not placements:
            return None
        target_count = len(placements[0].target_ids)
        return (0 if target_count > 1 else 2, -target_count, option.id)
    if option.kind == "attack":
        return (1, 0, option.id) if _attack_target(owner, setup, option) is not None else None
    if option.kind == "save":
        return (2, 0, option.id) if _single_save_target(owner, setup, option) is not None else None
    if option.kind == "ability_check":
        return (3, 0, option.id)
    return None


def _resolve_ability_check(
    sequence: int,
    round_number: int,
    owner: EncounterCombatant,
    option: LegendaryActionOption,
    dice: DiceProvider,
) -> BattleEvent:
    ability = option.check_ability or "wisdom"
    score = getattr(owner.state.template.ability_scores, ability, 10) if owner.state.template.ability_scores else 10
    bonus = (score - 10) // 2
    if option.check_skill:
        bonus = owner.state.template.skill_bonuses.get(option.check_skill, bonus)
    rolled = dice.roll(20)
    check = DiceRoll(
        notation=f"1d20+{bonus}", rolls=[rolled], selected_roll=rolled,
        modifier=bonus, mode=RollMode.NORMAL, total=rolled + bonus,
    )
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=owner.combatant_id,
        actor_name=owner.state.template.name,
        ability_check_roll=check,
        check_ability=ability,
        feature_id=option.id,
        animation="legendary-action",
        description=f"{owner.state.template.name} uses legendary action {option.name}: {ability.title()} check {check.total}.",
    )


def resolve_legendary_action(
    sequence: int,
    round_number: int,
    owner: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Resolve at most one deterministic legendary option for one owner."""
    choices = [
        (priority, option)
        for option in owner.state.template.legendary_actions
        if (priority := _priority(owner, setup, option)) is not None
    ]
    if not choices:
        return [], sequence
    _, option = min(choices, key=lambda item: item[0])
    events: list[BattleEvent]
    if option.kind == "attack":
        selected = _attack_target(owner, setup, option)
        if selected is None:
            return [], sequence
        target, attack, distance = selected
        events = [resolve_attack(
            sequence, round_number, owner.state, target.state, attack, distance, dice,
            actor_event_id=owner.combatant_id, target_event_id=target.combatant_id,
            spend_action=False, close_enemy_active=False, off_turn=True,
            affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
        )]
        sequence += 1
    elif option.kind == "save" and option.save_action is not None:
        action = option.save_action
        if action.area is not None:
            events, sequence, _ = resolve_area_save_action(
                sequence, round_number, owner, setup, action, dice, spend_action=False,
            )
        else:
            selected = _single_save_target(owner, setup, option)
            if selected is None:
                return [], sequence
            target, distance = selected
            events = [resolve_save_action(
                sequence, round_number, owner, target, action, distance, dice,
                spend_action=False, check_resource=False, spend_resource=False,
                affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
                setup=setup,
            )]
            sequence += 1
    else:
        events = [_resolve_ability_check(sequence, round_number, owner, option, dice)]
        sequence += 1
    remaining = spend_resource(owner.state, LEGENDARY_ACTION_RESOURCE_ID, option.cost)
    if events:
        events[-1].resource_remaining = remaining
        events[-1].description += f" Legendary Actions remaining: {remaining}."
    return events, sequence


def resolve_end_turn_legendary_actions(
    sequence: int,
    round_number: int,
    ended_member: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    """Each eligible creature may take one legendary option at the end of another creature's turn."""
    events: list[BattleEvent] = []
    members = [*setup.heroes, *setup.monsters]
    for owner in members:
        state = owner.state
        if owner.combatant_id == ended_member.combatant_id:
            continue
        if not state.template.legendary_actions or state.current_hp <= 0 or state.is_dead or not state.is_alive:
            continue
        if is_incapacitated(state):
            continue
        if not resource_available(state, LEGENDARY_ACTION_RESOURCE_ID):
            continue
        resolved, sequence = resolve_legendary_action(sequence, round_number, owner, setup, dice)
        events.extend(resolved)
    return events, sequence
