from __future__ import annotations

from app.combat.action_economy import spend
from app.combat.ally_context import pack_tactics_active
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.opportunity_attack_rules import MovementSource, opportunity_attack_weapon, unarmed_opportunity_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageType, Weapon, WeaponAttack, WeaponAttackKind


def _unarmed_damage_attack(reactor: EncounterCombatant) -> WeaponAttack:
    profile = reactor.state.template.unarmed_opportunity_attack
    if profile is None:
        raise ValueError("Combatant has no certified Unarmed Strike profile.")
    return WeaponAttack(
        id="unarmed-strike-damage",
        weapon=Weapon(
            id="unarmed-strike", name="Unarmed Strike", attack_kind=WeaponAttackKind.MELEE,
            dice_count=0, dice_size=2, damage_type=DamageType.BLUDGEONING,
            animation="strike", reach_ft=5,
        ),
        attack_bonus=profile.attack_bonus, damage_bonus=0, fixed_damage=profile.damage,
    )


def resolve_opportunity_attack(
    sequence: int, round_number: int, reactor: EncounterCombatant, mover: EncounterCombatant,
    setup: EncounterSetup, distance_before_ft: int, distance_after_ft: int,
    movement_source: MovementSource, dice: DiceProvider, *,
    disengaged: bool = False, can_see: bool = True, turn_key: str | None = None,
) -> BattleEvent | None:
    """Resolve a 2024 OA on the mover's active turn with a legal melee option."""
    attack = opportunity_attack_weapon(
        reactor, mover, distance_before_ft, distance_after_ft, movement_source,
        disengaged=disengaged, can_see=can_see,
    )
    if attack is None and unarmed_opportunity_available(
        reactor, mover, distance_before_ft, distance_after_ft, movement_source,
        disengaged=disengaged, can_see=can_see,
    ):
        attack = _unarmed_damage_attack(reactor)
    if attack is None:
        return None
    spend(reactor.state, "reaction")
    pack = pack_tactics_active(reactor, mover, setup)
    return resolve_encounter_attack(
        sequence, round_number, reactor, mover, attack, distance_before_ft, dice, setup,
        spend_action=False, advantage_sources=1 if pack else 0,
        feature_id="opportunity-attack", close_enemy_active=True, turn_key=turn_key,
    )
