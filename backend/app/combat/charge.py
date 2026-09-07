from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.charge_follow_up import resolve_charge_follow_up
from app.combat.charge_profiles import ChargeProfile, charge_profile_for_attack_id
from app.combat.death_triggers import resolve_pending_death_triggers
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.opening_burst import opening_burst_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, WeaponAttack
from app.domain.size import size_at_most
from app.domain.weapons import ChargeDefinition

ChargeData = ChargeDefinition | ChargeProfile


def _profile(attack: WeaponAttack) -> ChargeData | None:
    """Prefer declarative attack data; id lookup exists only until generated artifacts migrate."""
    return attack.charge or charge_profile_for_attack_id(attack.id)


def _charge_attack(attacker: CombatantState) -> WeaponAttack | None:
    attacks = [attacker.template.weapon_attack, *attacker.template.alternate_weapon_attacks]
    return next((attack for attack in attacks if _profile(attack) is not None), None)


def _target_size_allowed(defender: CombatantState, profile: ChargeData) -> bool:
    return profile.max_target_size is None or size_at_most(defender.template.size, profile.max_target_size)


def charge_profile(attacker: CombatantState, defender: CombatantState, attack: WeaponAttack, movement_ft: int) -> ChargeData | None:
    profile = _profile(attack)
    if profile is None or movement_ft < profile.minimum_move_ft or not _target_size_allowed(defender, profile): return None
    return profile


def charge_can_close(attacker: CombatantState, defender: CombatantState, attack: WeaponAttack, distance_ft: int, *, assume_precontact_runup: bool = False) -> bool:
    profile = _profile(attack)
    if not is_available(attacker, "action") or profile is None: return False
    enough_runup = assume_precontact_runup or distance_ft >= profile.minimum_move_ft
    return enough_runup and attacker.template.speed_ft >= profile.minimum_move_ft and _target_size_allowed(defender, profile)


def _bonus_damage(profile: ChargeData):
    if profile.bonus_damage is None: return None
    rider = profile.bonus_damage
    return ("Charge", rider.dice_count, rider.dice_size, rider.damage_type)


def _charged_attack(attack: WeaponAttack, profile: ChargeData) -> WeaponAttack:
    updates: dict[str, object] = {}
    if profile.prone_max_target_size is not None: updates["knocks_prone_max_size"] = profile.prone_max_target_size
    replacement = profile.replacement_damage
    if replacement is not None:
        updates["weapon"] = attack.weapon.model_copy(update={"dice_count": replacement.dice_count, "dice_size": replacement.dice_size, "damage_type": replacement.damage_type})
        updates["damage_bonus"] = replacement.damage_bonus; updates["fixed_damage"] = None
    return attack.model_copy(update=updates)


def resolve_charge_closing(
    sequence: int, round_number: int, attacker: EncounterCombatant, target: EncounterCombatant,
    dice: DiceProvider, setup: EncounterSetup | None = None,
) -> tuple[list[BattleEvent], int, bool]:
    """Resolve an eligible opening Charge from declarative attack parameters."""
    attack = _charge_attack(attacker.state)
    if attack is None or not opening_burst_available(round_number, attacker, setup): return [], sequence, False
    profile = _profile(attack)
    if profile is None or not charge_can_close(attacker.state, target.state, attack, profile.minimum_move_ft, assume_precontact_runup=True): return [], sequence, False
    profile = charge_profile(attacker.state, target.state, attack, profile.minimum_move_ft)
    if profile is None: return [], sequence, False
    event = resolve_encounter_attack(
        sequence, round_number, attacker, target, _charged_attack(attack, profile), attack.weapon.reach_ft,
        dice, setup, feature_id="charge", bonus_damage=_bonus_damage(profile),
    )
    events = [event]; sequence += 1
    if setup is not None:
        triggered, sequence = resolve_pending_death_triggers(sequence, round_number, setup, dice); events.extend(triggered)
    if attacker.state.is_dead or attacker.state.is_unconscious: return events, sequence, True
    follow_events, sequence = resolve_charge_follow_up(sequence, round_number, attacker, target, profile, event, dice, setup)
    events.extend(follow_events)
    if setup is not None:
        triggered, sequence = resolve_pending_death_triggers(sequence, round_number, setup, dice); events.extend(triggered)
    return events, sequence, True
