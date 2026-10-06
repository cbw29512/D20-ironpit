from __future__ import annotations

from typing import Any

from app.combat.conditions import apply_hit_conditions
from app.combat.deferred_save_effect import arm_deferred_save_effect
from app.combat.exile import apply_on_hit_exile
from app.combat.melee_hit_retaliation import apply_melee_hit_retaliation
from app.combat.melee_hit_save_retaliation import apply_melee_hit_save_retaliation
from app.combat.on_hit_condition_save import resolve_on_hit_condition_save
from app.combat.on_hit_contested_movement import resolve_on_hit_contested_movement
from app.combat.on_hit_maximum_hp_save import resolve_on_hit_maximum_hp_save
from app.combat.post_hit_spell_riders import resolve_paid_post_hit_spell_riders
from app.combat.sap import apply_weapon_sap
from app.combat.slow import apply_weapon_slow
from app.combat.tactical_master import apply_tactical_master_sap
from app.combat.topple import resolve_topple_hit
from app.combat.vex import apply_vex_mastery


def resolve_attack_hit_riders(
    result: Any,
    attacker,
    defender,
    attack,
    dice,
    *,
    round_number: int,
    attacker_event_id: str,
    defender_event_id: str,
    actual_event_id: str,
    active_turn_key: str,
    affected_states,
    setup,
) -> None:
    if result.cunning_strike.applied:
        result.applied_conditions.append("prone")
    if result.cunning_strike_obscure.applied:
        result.applied_conditions.append("blinded")
    result.applied_conditions.extend(
        apply_hit_conditions(
            attack,
            defender,
            attacker_event_id,
            round_number,
            affected_states,
            attacker.template,
        )
    )
    result.on_hit_save = resolve_on_hit_condition_save(
        defender,
        attack,
        dice,
        attacker.template,
        source_id=attacker_event_id,
        round_number=round_number,
        affected_states=affected_states,
        setup=setup,
        target_id=actual_event_id,
    )
    damage_taken = sum(
        component.applied_total or 0 for component in result.damage_components
    )
    result.on_hit_maximum_hp_save = resolve_on_hit_maximum_hp_save(
        defender, attack, dice, damage_taken
    )
    if attack.on_hit_contested_movement is not None:
        if setup is None:
            raise ValueError("Contested forced movement requires encounter setup.")
        members = {
            item.combatant_id: item for item in [*setup.heroes, *setup.monsters]
        }
        source_member = members.get(attacker_event_id)
        target_member = members.get(actual_event_id)
        if source_member is None or target_member is None:
            raise ValueError(
                "Contested forced movement combatants are missing from encounter setup."
            )
        result.contested_movement = resolve_on_hit_contested_movement(
            source_member,
            target_member,
            attack,
            dice,
            setup,
            round_number=round_number,
        )
    if (
        result.on_hit_save.applied_condition
        and result.on_hit_save.applied_condition not in result.applied_conditions
    ):
        result.applied_conditions.append(result.on_hit_save.applied_condition)

    result.topple = resolve_topple_hit(attacker, defender, attack, dice)
    if result.topple.applied and "prone" not in result.applied_conditions:
        result.applied_conditions.append("prone")
    result.weapon_sap_applied = apply_weapon_sap(
        attacker, attacker_event_id, defender, attack, round_number
    )
    result.weapon_slow_applied = apply_weapon_slow(
        attacker, attacker_event_id, defender, attack, round_number
    )
    if not result.weapon_sap_applied:
        result.tactical_sap_applied = apply_tactical_master_sap(
            attacker, attacker_event_id, defender, attack, round_number
        )
    applied_total = sum(
        component.applied_total or 0 for component in result.damage_components
    )
    result.vex_applied = apply_vex_mastery(
        attacker,
        attacker_event_id,
        actual_event_id,
        attack,
        round_number,
        applied_total,
    )
    result.deferred_effect_armed = arm_deferred_save_effect(
        attacker, defender, actual_event_id, attack, round_number
    )
    result.exile_applied = apply_on_hit_exile(
        attacker,
        defender,
        attack,
        attacker_id=attacker_event_id,
        round_number=round_number,
        affected_states=affected_states,
        dice=dice,
        turn_key=active_turn_key,
    )
    if setup is None:
        return
    members = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
    attacker_member = members.get(attacker_event_id)
    defender_member = members.get(defender_event_id)
    if attacker_member is None or defender_member is None:
        return
    result.applied_conditions.extend(
        resolve_paid_post_hit_spell_riders(
            attacker_member,
            defender_member,
            setup,
            dice,
            round_number=round_number,
            turn_key=active_turn_key,
            affected_states=affected_states,
        )
    )
    melee = attack.weapon.attack_kind.value == "melee"
    apply_melee_hit_retaliation(
        attacker_member,
        defender_member,
        melee=melee,
        dice=dice,
        affected_states=affected_states,
    )
    apply_melee_hit_save_retaliation(
        attacker_member,
        defender_member,
        melee=melee,
        dice=dice,
        setup=setup,
        round_number=round_number,
        affected_states=affected_states,
    )
