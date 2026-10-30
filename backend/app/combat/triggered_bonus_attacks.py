from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.attack_legality import attack_allowed_against, attack_available_for_source
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.hit_points import effective_max_hp
from app.combat.resources import resource_available, spend_resource
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack
from app.domain.weapons import WeaponAttackKind

logger = logging.getLogger(__name__)


def _attack_by_id(member: EncounterCombatant, attack_id: str) -> WeaponAttack:
    try:
        attacks = [member.state.template.weapon_attack, *member.state.template.alternate_weapon_attacks]
        matches = [attack for attack in attacks if attack.id == attack_id]
        if len(matches) != 1:
            raise ValueError(f"Expected one attack {attack_id!r}; found {len(matches)}.")
        return matches[0]
    except Exception as exc:
        logger.exception("Failed to resolve triggered attack %s for %s.", attack_id, member.combatant_id)
        raise RuntimeError("Triggered attack binding could not be resolved.") from exc


def _in_range(attack: WeaponAttack, distance_ft: int) -> bool:
    try:
        kind = attack.weapon.attack_kind
        if kind in {WeaponAttackKind.MELEE, WeaponAttackKind.MELEE_OR_RANGED} and distance_ft <= attack.weapon.reach_ft:
            return True
        if kind in {WeaponAttackKind.RANGED, WeaponAttackKind.MELEE_OR_RANGED}:
            return attack.weapon.long_range_ft is not None and distance_ft <= attack.weapon.long_range_ft
        return False
    except Exception as exc:
        logger.exception("Failed triggered attack range check for %s.", attack.id)
        raise RuntimeError("Triggered attack range could not be evaluated.") from exc


def _qualifying_event(
    source: EncounterCombatant,
    setup: EncounterSetup,
    events: list[BattleEvent],
) -> BattleEvent | None:
    try:
        members = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
        for event in reversed(events):
            if event.actor_id != source.combatant_id or event.event_type != "attack":
                continue
            if event.damage_roll is None or event.damage_roll.total <= 0 or event.hp_before is None:
                continue
            target = members.get(event.target_id or "")
            if target is None:
                continue
            max_hp_before = event.max_hp_before or effective_max_hp(target.state)
            if event.hp_before * 2 <= max_hp_before:
                return event
        return None
    except Exception as exc:
        logger.exception("Failed triggered Bonus Action event scan for %s.", source.combatant_id)
        raise RuntimeError("Triggered Bonus Action event scan failed.") from exc


def resolve_triggered_bonus_attack(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    dice,
    turn_events: list[BattleEvent],
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    try:
        if not is_available(source.state, "bonus_action"):
            return [], sequence
        trigger_event = _qualifying_event(source, setup, turn_events)
        if trigger_event is None:
            return [], sequence

        members = [*setup.heroes, *setup.monsters]
        by_id = {member.combatant_id: member for member in members}
        for feature in source.state.template.triggered_bonus_attacks:
            if feature.trigger != "damage_target_already_bloodied":
                raise ValueError(f"Unsupported triggered Bonus Action trigger: {feature.trigger}.")
            if not resource_available(source.state, feature.resource_id, feature.resource_cost):
                continue
            attack = _attack_by_id(source, feature.attack_id)
            candidates = []
            original = by_id.get(trigger_event.target_id or "")
            if original is not None:
                candidates.append(original)
            candidates.extend(
                member for member in members
                if member.side != source.side and member not in candidates
            )
            target = next((
                member for member in candidates
                if member.state.is_alive and not member.state.is_dead
                and attack_available_for_source(attack, source.state)
                and attack_allowed_against(attack, source.combatant_id, member.state)
                and _in_range(attack, combatant_distance(source, member))
            ), None)
            if target is None:
                return [], sequence

            spend(source.state, "bonus_action")
            remaining = spend_resource(source.state, feature.resource_id, feature.resource_cost)
            event = resolve_encounter_attack(
                sequence, round_number, source, target, attack,
                combatant_distance(source, target), dice, setup,
                spend_action=False, feature_id=feature.id, turn_key=turn_key,
            )
            event.resource_remaining = remaining
            return [event], sequence + 1
        return [], sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Triggered Bonus Action attack failed for %s.", source.combatant_id)
        raise RuntimeError("Triggered Bonus Action attack resolution failed.") from exc
