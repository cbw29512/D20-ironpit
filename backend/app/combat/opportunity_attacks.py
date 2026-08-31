from __future__ import annotations

from typing import Literal

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.policy import weapon_attack_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack, WeaponAttackKind

MovementSource = Literal["speed", "action", "bonus_action", "reaction", "forced", "teleport"]
_PROVOKING_SOURCES = frozenset({"speed", "action", "bonus_action", "reaction"})


def _melee_departure_attack(
    reactor: EncounterCombatant,
    distance_before_ft: int,
    distance_after_ft: int,
) -> WeaponAttack | None:
    """Choose one physical melee profile whose reach is actually being left."""
    for attack in weapon_attack_profiles(reactor.state):
        weapon = attack.weapon
        if weapon.attack_kind is not WeaponAttackKind.MELEE:
            continue
        if distance_before_ft <= weapon.reach_ft < distance_after_ft:
            return attack
    return None


def resolve_opportunity_attack(
    sequence: int,
    round_number: int,
    reactor: EncounterCombatant,
    mover: EncounterCombatant,
    setup: EncounterSetup,
    distance_before_ft: int,
    distance_after_ft: int,
    movement_source: MovementSource,
    dice: DiceProvider,
    *,
    disengaged: bool = False,
    can_see: bool = True,
) -> BattleEvent | None:
    """Resolve the universal 2024 Opportunity Attack Reaction immediately before reach is left."""
    if reactor.side == mover.side or not can_see or disengaged:
        return None
    if movement_source not in _PROVOKING_SOURCES or not is_available(reactor.state, "reaction"):
        return None
    attack = _melee_departure_attack(reactor, distance_before_ft, distance_after_ft)
    if attack is None:
        return None
    spend(reactor.state, "reaction")
    pack = pack_tactics_active(reactor, mover, setup)
    return resolve_encounter_attack(
        sequence, round_number, reactor, mover, attack, distance_before_ft, dice, setup,
        spend_action=False, advantage_sources=1 if pack else 0,
        feature_id="opportunity-attack", close_enemy_active=True,
    )
