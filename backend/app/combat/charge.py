from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.charge_follow_up import resolve_charge_follow_up
from app.combat.charge_profiles import ChargeDamage, ChargeProfile, charge_profile_for_attack_id
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.opening_burst import opening_burst_available
from app.combat.reaction_movement import move_toward_with_reactions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, WeaponAttack
from app.domain.size import size_at_most
from app.domain.traits import CombatTrait


def _charge_attack(attacker: CombatantState) -> WeaponAttack | None:
    attacks = [attacker.template.weapon_attack, *attacker.template.alternate_weapon_attacks]
    return next((attack for attack in attacks if charge_profile_for_attack_id(attack.id) is not None), None)


def _target_size_allowed(defender: CombatantState, profile: ChargeProfile) -> bool:
    return profile.max_target_size is None or size_at_most(defender.template.size, profile.max_target_size)


def charge_profile(
    attacker: CombatantState, defender: CombatantState, attack: WeaponAttack, movement_ft: int,
) -> ChargeProfile | None:
    if CombatTrait.CHARGE not in attacker.template.combat_traits:
        return None
    profile = charge_profile_for_attack_id(attack.id)
    if profile is None or movement_ft < profile.minimum_move_ft or not _target_size_allowed(defender, profile):
        return None
    return profile


def charge_can_close(
    attacker: CombatantState, defender: CombatantState, attack: WeaponAttack, distance_ft: int,
    *, assume_precontact_runup: bool = False,
) -> bool:
    profile = charge_profile_for_attack_id(attack.id)
    if not is_available(attacker, "action") or CombatTrait.CHARGE not in attacker.template.combat_traits or profile is None:
        return False
    needed = max(0, distance_ft - attack.weapon.reach_ft)
    enough_runup = assume_precontact_runup or needed >= profile.minimum_move_ft
    return enough_runup and needed <= attacker.movement_remaining_ft and _target_size_allowed(defender, profile)


def _bonus_damage(profile: ChargeProfile):
    if profile.bonus_damage is None:
        return None
    rider = profile.bonus_damage
    return ("Charge", rider.dice_count, rider.dice_size, rider.damage_type)


def _charged_attack(attack: WeaponAttack, profile: ChargeProfile) -> WeaponAttack:
    updates: dict[str, object] = {}
    if profile.prone_max_target_size is not None:
        updates["knocks_prone_max_size"] = profile.prone_max_target_size
    replacement = profile.replacement_damage
    if replacement is not None:
        updates["weapon"] = attack.weapon.model_copy(update={
            "dice_count": replacement.dice_count,
            "dice_size": replacement.dice_size,
            "damage_type": replacement.damage_type,
        })
        updates["damage_bonus"] = replacement.damage_bonus
        updates["fixed_damage"] = None
    return attack.model_copy(update=updates)


def resolve_charge_closing(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    dice: DiceProvider,
    setup: EncounterSetup | None = None,
) -> tuple[list[BattleEvent], int, bool]:
    attack = _charge_attack(attacker.state)
    if attack is None or not opening_burst_available(round_number, attacker, setup):
        return [], sequence, False
    if not charge_can_close(
        attacker.state, target.state, attack, combatant_distance(attacker, target),
        assume_precontact_runup=True,
    ):
        return [], sequence, False

    profile = charge_profile_for_attack_id(attack.id)
    if profile is None:
        return [], sequence, False
    move_events: list[BattleEvent] = []
    movement_ft = profile.minimum_move_ft
    if combatant_distance(attacker, target) > attack.weapon.reach_ft:
        move_events, sequence, movement = move_toward_with_reactions(
            sequence, round_number, attacker, target, setup, attack.weapon.reach_ft, dice,
        )
        if movement is None:
            return move_events, sequence, bool(move_events)
        movement_ft = max(movement_ft, movement.movement_ft or 0)
    profile = charge_profile(attacker.state, target.state, attack, movement_ft)
    if profile is None:
        return move_events, sequence, bool(move_events)

    event = resolve_encounter_attack(
        sequence, round_number, attacker, target, _charged_attack(attack, profile),
        combatant_distance(attacker, target), dice, setup,
        feature_id="charge", bonus_damage=_bonus_damage(profile),
    )
    sequence += 1
    follow_events, sequence = resolve_charge_follow_up(
        sequence, round_number, attacker, target, profile, event, dice, setup,
    )
    return [*move_events, event, *follow_events], sequence, True
