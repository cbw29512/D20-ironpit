from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.damage import aggregate_damage_components, roll_damage_component
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.zero_hp import apply_damage
from app.domain.attachments import AttachmentState
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def apply_attachment(
    source: CombatantState, source_id: str, target_id: str,
    attack: WeaponAttack, round_number: int,
) -> bool:
    try:
        rule = attack.attachment_on_hit
        if rule is None:
            return False
        source.attachment = AttachmentState(
            source_id=source_id, target_id=target_id, source_effect_id=attack.id,
            applied_round=round_number,
            periodic_damage_count=rule.periodic_damage_count,
            periodic_damage_size=rule.periodic_damage_size,
            periodic_damage_bonus=rule.periodic_damage_bonus,
            periodic_damage_type=rule.periodic_damage_type,
            forbids_source_attack_ids=rule.forbids_source_attack_ids,
            detachable_by_source_movement_ft=rule.detachable_by_source_movement_ft,
            detachable_by_target_action=rule.detachable_by_target_action,
            detachable_by_adjacent_action=rule.detachable_by_adjacent_action,
        )
        return True
    except Exception as exc:
        logger.exception("Failed to apply attachment from %s.", source_id)
        raise RuntimeError("Attachment could not be applied.") from exc


def attached_source_for(target_id: str, setup: EncounterSetup) -> EncounterCombatant | None:
    try:
        return next((member for member in members(setup)
                     if member.state.attachment and member.state.attachment.target_id == target_id), None)
    except Exception as exc:
        logger.exception("Failed to locate attachment source for %s.", target_id)
        raise RuntimeError("Attachment source could not be resolved.") from exc


def resolve_detach_action(
    sequence: int, round_number: int, actor: EncounterCombatant, setup: EncounterSetup,
) -> BattleEvent | None:
    try:
        if not is_available(actor.state, "action"):
            return None
        all_members = members(setup)
        for source in all_members:
            relation = source.state.attachment
            if relation is None:
                continue
            target = next((member for member in all_members if member.combatant_id == relation.target_id), None)
            if target is None or target.side != actor.side:
                continue
            target_detach = actor.combatant_id == target.combatant_id and relation.detachable_by_target_action
            adjacent_detach = (
                actor.combatant_id != target.combatant_id
                and relation.detachable_by_adjacent_action
                and combatant_distance(actor, target) <= 5
            )
            if not (target_detach or adjacent_detach):
                continue
            source.state.attachment = None
            spend(actor.state, "action")
            return BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=actor.combatant_id, actor_name=actor.state.template.name,
                target_id=source.combatant_id, target_name=source.state.template.name,
                feature_id="detach-attachment", animation="detach",
                description=f"{actor.state.template.name} detaches {source.state.template.name}.",
            )
        return None
    except Exception as exc:
        logger.exception("Failed detach action for %s.", actor.combatant_id)
        raise RuntimeError("Attachment detach action could not be resolved.") from exc


def detach_source_by_movement(source: CombatantState) -> int:
    try:
        relation = source.attachment
        if relation is None or relation.detachable_by_source_movement_ft is None:
            return 0
        cost = relation.detachable_by_source_movement_ft
        if source.movement_remaining_ft < cost:
            return 0
        source.movement_remaining_ft -= cost
        source.attachment = None
        return cost
    except Exception as exc:
        logger.exception("Failed source movement detach for %s.", source.template.name)
        raise RuntimeError("Source movement detach could not be resolved.") from exc


def resolve_attachment_start_turn(
    sequence: int, round_number: int, source: EncounterCombatant,
    setup: EncounterSetup, dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    try:
        relation = source.state.attachment
        if relation is None:
            return [], sequence
        target = next((member for member in members(setup) if member.combatant_id == relation.target_id), None)
        if target is None or source.state.is_dead or not source.state.is_alive or target.state.is_dead:
            source.state.attachment = None
            return [], sequence
        component = roll_damage_component(
            dice, source.state.template.name, relation.periodic_damage_count,
            relation.periodic_damage_size, relation.periodic_damage_bonus,
            relation.periodic_damage_type, False,
        )
        total, components = apply_damage_defenses(target.state, [component])
        hp_before = target.state.current_hp
        affected_states = [member.state for member in members(setup)]
        apply_damage(
            target.state, total, damage_types={relation.periodic_damage_type},
            dice=dice, affected_states=affected_states,
        )
        event = BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature",
            actor_id=source.combatant_id, actor_name=source.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            feature_id=relation.source_effect_id,
            damage_roll=aggregate_damage_components(components), damage_components=components,
            hp_before=hp_before, hp_after=target.state.current_hp, animation="attachment-damage",
            description=(f"{source.state.template.name}'s attached effect deals {total} "
                         f"{relation.periodic_damage_type.value} damage to {target.state.template.name}."),
        )
        if target.state.is_dead:
            source.state.attachment = None
        return [event], sequence + 1
    except Exception as exc:
        logger.exception("Failed attachment start-turn resolution for %s.", source.combatant_id)
        raise RuntimeError("Attachment start-turn effect could not be resolved.") from exc
