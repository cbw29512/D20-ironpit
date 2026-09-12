from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.charge_follow_up import resolve_charge_follow_up
from app.combat.charge_profiles import ChargeProfile, charge_profile_for_attack_id
from app.combat.charge_prone import resolve_charge_prone
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.opening_burst import opening_burst_available
from app.domain.charge_profiles import ChargeProfileDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, DamageType, WeaponAttack
from app.domain.size import size_at_most
from app.domain.traits import CombatTrait

ChargeProfileLike = ChargeProfileDefinition | ChargeProfile


def _profile_for_attack(attack: WeaponAttack) -> ChargeProfileLike | None:
    return attack.charge_profile or charge_profile_for_attack_id(attack.id)


def _charge_attack(attacker: CombatantState) -> WeaponAttack | None:
    attacks = [attacker.template.weapon_attack, *attacker.template.alternate_weapon_attacks]
    return next((attack for attack in attacks if _profile_for_attack(attack) is not None), None)


def _target_size_allowed(defender: CombatantState, profile: ChargeProfileLike) -> bool:
    return profile.max_target_size is None or size_at_most(defender.template.size, profile.max_target_size)


def charge_profile(
    attacker: CombatantState, defender: CombatantState, attack: WeaponAttack, movement_ft: int,
) -> ChargeProfileLike | None:
    if CombatTrait.CHARGE not in attacker.template.combat_traits:
        return None
    profile = _profile_for_attack(attack)
    if profile is None or movement_ft < profile.minimum_move_ft or not _target_size_allowed(defender, profile):
        return None
    return profile


def charge_can_close(
    attacker: CombatantState, defender: CombatantState, attack: WeaponAttack, distance_ft: int,
    *, assume_precontact_runup: bool = False,
) -> bool:
    profile = _profile_for_attack(attack)
    if not is_available(attacker, "action") or CombatTrait.CHARGE not in attacker.template.combat_traits or profile is None:
        return False
    enough_runup = assume_precontact_runup or distance_ft >= profile.minimum_move_ft
    return enough_runup and attacker.template.speed_ft >= profile.minimum_move_ft and _target_size_allowed(defender, profile)


def _bonus_damage(profile: ChargeProfileLike):
    if profile.bonus_damage is None:
        return None
    rider = profile.bonus_damage
    return ("Charge", rider.dice_count, rider.dice_size, DamageType(rider.damage_type))


def _charged_attack(attack: WeaponAttack, profile: ChargeProfileLike) -> WeaponAttack:
    updates: dict[str, object] = {}
    if profile.prone_max_target_size is not None and getattr(profile, "prone_save_dc", None) is None:
        updates["knocks_prone_max_size"] = profile.prone_max_target_size
    replacement = profile.replacement_damage
    if replacement is not None:
        updates["weapon"] = attack.weapon.model_copy(update={
            "dice_count": replacement.dice_count,
            "dice_size": replacement.dice_size,
            "damage_type": DamageType(replacement.damage_type),
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
    """Resolve an eligible round-1 Charge using abstracted pre-contact run-up; cards never move."""
    attack = _charge_attack(attacker.state)
    if attack is None or not opening_burst_available(round_number, attacker, setup):
        return [], sequence, False
    profile = _profile_for_attack(attack)
    if profile is None or not charge_can_close(
        attacker.state, target.state, attack, profile.minimum_move_ft,
        assume_precontact_runup=True,
    ):
        return [], sequence, False
    profile = charge_profile(attacker.state, target.state, attack, profile.minimum_move_ft)
    if profile is None:
        return [], sequence, False

    event = resolve_encounter_attack(
        sequence, round_number, attacker, target, _charged_attack(attack, profile),
        attack.weapon.reach_ft, dice, setup,
        feature_id="charge", bonus_damage=_bonus_damage(profile),
    )
    if isinstance(profile, ChargeProfileDefinition):
        event = resolve_charge_prone(event, target, profile, dice, setup)
    sequence += 1
    follow_events, sequence = resolve_charge_follow_up(
        sequence, round_number, attacker, target, profile, event, dice, setup,
    )
    return [event, *follow_events], sequence, True
