from __future__ import annotations

import logging
from dataclasses import dataclass

from app.combat.action_economy import is_available, spend
from app.combat.area_targeting import AreaPlacement, legal_area_placements
from app.combat.condition_rules import is_incapacitated
from app.combat.damage_reaction_events import resolve_damage_event_reactions
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.domain.area_weapon_attacks import AreaWeaponAttackAction
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AreaWeaponAttackChoice:
    action: AreaWeaponAttackAction
    attack: WeaponAttack
    placement: AreaPlacement


def _attack_by_id(member: EncounterCombatant, attack_id: str) -> WeaponAttack:
    attacks = [member.state.template.weapon_attack, *member.state.template.alternate_weapon_attacks]
    attack = next((item for item in attacks if item.id == attack_id), None)
    if attack is None:
        raise ValueError(f"Unknown area-weapon attack id {attack_id!r}.")
    return attack


def _legal_target_ids(
    member: EncounterCombatant,
    setup: EncounterSetup,
    attack: WeaponAttack,
    placement: AreaPlacement,
) -> tuple[str, ...]:
    members = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
    maximum = attack.weapon.long_range_ft or attack.weapon.normal_range_ft or attack.weapon.reach_ft
    return tuple(
        target_id for target_id in placement.target_ids
        if target_id in members and combatant_distance(member, members[target_id]) <= maximum
    )


def choose_area_weapon_attack(
    member: EncounterCombatant,
    setup: EncounterSetup,
    *,
    require_action: bool = True,
) -> AreaWeaponAttackChoice | None:
    try:
        if require_action and not is_available(member.state, "action"):
            return None
        normal_count = len(member.state.template.attack_action.slots) if member.state.template.attack_action else 1
        choices: list[AreaWeaponAttackChoice] = []
        for action in member.state.template.area_weapon_attack_actions:
            attack = _attack_by_id(member, action.attack_id)
            for placement in legal_area_placements(member, setup, action.area, action.range_ft):
                legal_ids = _legal_target_ids(member, setup, attack, placement)
                if len(legal_ids) <= normal_count:
                    continue
                choices.append(AreaWeaponAttackChoice(
                    action=action,
                    attack=attack,
                    placement=AreaPlacement(
                        target_ids=legal_ids,
                        origin=placement.origin,
                        direction=placement.direction,
                        friendly_ids=placement.friendly_ids,
                    ),
                ))
        return max(choices, key=lambda item: len(item.placement.target_ids), default=None)
    except Exception:
        logger.exception("Failed to choose area weapon attack for %s.", member.combatant_id)
        raise


def resolve_area_weapon_attack(
    sequence: int,
    round_number: int,
    member: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    choice: AreaWeaponAttackChoice,
) -> tuple[list[BattleEvent], int]:
    try:
        if not is_available(member.state, "action"):
            raise ValueError("Area weapon attack requires an available Action.")
        spend(member.state, "action")
        by_id = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
        events: list[BattleEvent] = []
        turn_key = f"{round_number}:{member.combatant_id}"
        for target_id in choice.placement.target_ids:
            if member.state.turn_terminated or member.state.is_dead or is_incapacitated(member.state):
                break
            target = by_id.get(target_id)
            if target is None or target.state.is_dead or not target.state.is_alive:
                continue
            event = resolve_encounter_attack(
                sequence, round_number, member, target, choice.attack,
                combatant_distance(member, target), dice, setup,
                spend_action=False, feature_id=choice.action.id, turn_key=turn_key,
            )
            events.append(event)
            sequence += 1
            reactions, sequence = resolve_damage_event_reactions(
                sequence, round_number, member, event, setup, dice, turn_key=turn_key,
            )
            events.extend(reactions)
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Area weapon attack failed for %s.", member.combatant_id)
        raise RuntimeError("Area weapon attack could not be resolved.") from exc
