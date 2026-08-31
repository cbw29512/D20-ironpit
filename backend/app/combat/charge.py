from __future__ import annotations

from dataclasses import dataclass

from app.combat.action_economy import is_available
from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.opening_burst import opening_burst_available
from app.combat.reaction_movement import move_toward_with_reactions
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, DamageType, WeaponAttack
from app.domain.size import CreatureSize, size_at_most
from app.domain.traits import CombatTrait


@dataclass(frozen=True)
class ChargeProfile:
    attack_id: str
    minimum_move_ft: int
    dice_count: int
    dice_size: int
    damage_type: DamageType
    max_target_size: CreatureSize


_PROFILES = {
    "boar-gore": ChargeProfile("boar-gore", 20, 1, 6, DamageType.PIERCING, CreatureSize.MEDIUM),
    "elk-ram": ChargeProfile("elk-ram", 20, 1, 6, DamageType.BLUDGEONING, CreatureSize.LARGE),
    "giant-boar-gore": ChargeProfile("giant-boar-gore", 20, 2, 6, DamageType.PIERCING, CreatureSize.LARGE),
    "giant-goat-ram": ChargeProfile("giant-goat-ram", 20, 2, 4, DamageType.BLUDGEONING, CreatureSize.LARGE),
    "rhinoceros-gore": ChargeProfile("rhinoceros-gore", 20, 2, 8, DamageType.PIERCING, CreatureSize.LARGE),
    "warhorse-hooves": ChargeProfile("warhorse-hooves", 20, 2, 4, DamageType.BLUDGEONING, CreatureSize.LARGE),
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
    event = resolve_attack(
        sequence, round_number, attacker.state, target.state, charged_attack,
        combatant_distance(attacker, target), dice,
        actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
        feature_id="charge",
        bonus_damage=("Charge", profile.dice_count, profile.dice_size, profile.damage_type),
    )
    return [*move_events, event], sequence + 1, True
