from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.opening_burst import opening_burst_available
from app.combat.reaction_movement import move_toward_with_reactions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, DamageType, WeaponAttack
from app.domain.size import CreatureSize, size_at_most
from app.domain.traits import CombatTrait


@dataclass(frozen=True)
class ChargeDamage:
    dice_count: int
    dice_size: int
    damage_type: DamageType


@dataclass(frozen=True)
class ChargeProfile:
    attack_id: str
    minimum_move_ft: int
    max_target_size: CreatureSize
    bonus_damage: ChargeDamage | None = None


_PROFILES = {
    "boar-gore": ChargeProfile(
        "boar-gore", 20, CreatureSize.MEDIUM, ChargeDamage(1, 6, DamageType.PIERCING),
    ),
    "elk-ram": ChargeProfile(
        "elk-ram", 20, CreatureSize.LARGE, ChargeDamage(1, 6, DamageType.BLUDGEONING),
    ),
    "giant-boar-gore": ChargeProfile(
        "giant-boar-gore", 20, CreatureSize.LARGE, ChargeDamage(2, 6, DamageType.PIERCING),
    ),
    "giant-elk-ram": ChargeProfile(
        "giant-elk-ram", 20, CreatureSize.HUGE, ChargeDamage(2, 4, DamageType.BLUDGEONING),
    ),
    "giant-goat-ram": ChargeProfile(
        "giant-goat-ram", 20, CreatureSize.LARGE, ChargeDamage(2, 4, DamageType.BLUDGEONING),
    ),
    "minotaur-skeleton-gore": ChargeProfile(
        "minotaur-skeleton-gore", 20, CreatureSize.LARGE, ChargeDamage(2, 8, DamageType.PIERCING),
    ),
    "rhinoceros-gore": ChargeProfile(
        "rhinoceros-gore", 20, CreatureSize.LARGE, ChargeDamage(2, 8, DamageType.PIERCING),
    ),
    "triceratops-gore": ChargeProfile(
        "triceratops-gore", 20, CreatureSize.HUGE, ChargeDamage(2, 8, DamageType.PIERCING),
    ),
    "warhorse-hooves": ChargeProfile(
        "warhorse-hooves", 20, CreatureSize.LARGE, ChargeDamage(2, 4, DamageType.BLUDGEONING),
    ),
    "warhorse-skeleton-hooves": ChargeProfile(
        "warhorse-skeleton-hooves", 20, CreatureSize.LARGE,
    ),
}


def charge_profile_for_attack_id(attack_id: str) -> ChargeProfile | None:
    return _PROFILES.get(attack_id)


def charge_profile(
    attacker: CombatantState, defender: CombatantState, attack: WeaponAttack, movement_ft: int,
) -> ChargeProfile | None:
    if CombatTrait.CHARGE not in attacker.template.combat_traits:
        return None
    profile = charge_profile_for_attack_id(attack.id)
    if profile is None or movement_ft < profile.minimum_move_ft:
        return None
    return profile if size_at_most(defender.template.size, profile.max_target_size) else None


def charge_can_close(
    attacker: CombatantState, defender: CombatantState, attack: WeaponAttack, distance_ft: int,
    *, assume_precontact_runup: bool = False,
) -> bool:
    profile = charge_profile_for_attack_id(attack.id)
    if not is_available(attacker, "action") or CombatTrait.CHARGE not in attacker.template.combat_traits or profile is None:
        return False
    needed = max(0, distance_ft - attack.weapon.reach_ft)
    enough_runup = assume_precontact_runup or needed >= profile.minimum_move_ft
    return (
        enough_runup
        and needed <= attacker.movement_remaining_ft
        and size_at_most(defender.template.size, profile.max_target_size)
    )


def resolve_charge_closing(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    dice: DiceProvider,
    setup: EncounterSetup | None = None,
) -> tuple[list[BattleEvent], int, bool]:
    attack = attacker.state.template.weapon_attack
    if not opening_burst_available(round_number, attacker, setup):
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

    charged_attack = attack.model_copy(update={"knocks_prone_max_size": profile.max_target_size})
    bonus_damage = None
    if profile.bonus_damage is not None:
        rider = profile.bonus_damage
        bonus_damage = ("Charge", rider.dice_count, rider.dice_size, rider.damage_type)
    event = resolve_encounter_attack(
        sequence, round_number, attacker, target, charged_attack,
        combatant_distance(attacker, target), dice, setup,
        feature_id="charge", bonus_damage=bonus_damage,
    )
    return [*move_events, event], sequence + 1, True
