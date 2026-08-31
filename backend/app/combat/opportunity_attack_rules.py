from __future__ import annotations

from typing import Literal

from app.combat.action_economy import is_available
from app.combat.condition_rules import BLINDED, has_condition
from app.combat.policy import weapon_attack_profiles
from app.domain.encounters import EncounterCombatant
from app.domain.models import WeaponAttack, WeaponAttackKind

MovementSource = Literal["speed", "action", "bonus_action", "reaction", "forced", "teleport"]
_PROVOKING_SOURCES = frozenset({"speed", "action", "bonus_action", "reaction"})


def opportunity_attack_weapon(
    reactor: EncounterCombatant,
    mover: EncounterCombatant,
    distance_before_ft: int,
    distance_after_ft: int,
    movement_source: MovementSource,
    *,
    disengaged: bool = False,
    can_see: bool = True,
) -> WeaponAttack | None:
    """Return the legal modeled melee weapon for a 2024 Opportunity Attack, or None."""
    if reactor.side == mover.side or disengaged or not can_see or has_condition(reactor.state, BLINDED):
        return None
    if movement_source not in _PROVOKING_SOURCES or not is_available(reactor.state, "reaction"):
        return None
    for attack in weapon_attack_profiles(reactor.state):
        weapon = attack.weapon
        if weapon.attack_kind is WeaponAttackKind.MELEE and distance_before_ft <= weapon.reach_ft < distance_after_ft:
            return attack
    return None
