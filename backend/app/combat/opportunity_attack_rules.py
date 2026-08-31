from __future__ import annotations

from typing import Literal

from app.combat.action_economy import is_available
from app.combat.condition_rules import BLINDED, has_condition
from app.combat.policy import weapon_attack_profiles
from app.domain.encounters import EncounterCombatant
from app.domain.models import WeaponAttack, WeaponAttackKind

MovementSource = Literal["speed", "action", "bonus_action", "reaction", "forced", "teleport"]
_PROVOKING_SOURCES = frozenset({"speed", "action", "bonus_action", "reaction"})


def _can_react(
    reactor: EncounterCombatant, mover: EncounterCombatant, movement_source: MovementSource,
    *, disengaged: bool, can_see: bool,
) -> bool:
    return (
        reactor.side != mover.side and not disengaged and can_see
        and not has_condition(reactor.state, BLINDED)
        and movement_source in _PROVOKING_SOURCES
        and is_available(reactor.state, "reaction")
    )


def opportunity_attack_weapon(
    reactor: EncounterCombatant, mover: EncounterCombatant,
    distance_before_ft: int, distance_after_ft: int, movement_source: MovementSource,
    *, disengaged: bool = False, can_see: bool = True,
) -> WeaponAttack | None:
    if not _can_react(reactor, mover, movement_source, disengaged=disengaged, can_see=can_see):
        return None
    for attack in weapon_attack_profiles(reactor.state):
        weapon = attack.weapon
        if weapon.attack_kind is WeaponAttackKind.MELEE and distance_before_ft <= weapon.reach_ft < distance_after_ft:
            return attack
    return None


def unarmed_opportunity_available(
    reactor: EncounterCombatant, mover: EncounterCombatant,
    distance_before_ft: int, distance_after_ft: int, movement_source: MovementSource,
    *, disengaged: bool = False, can_see: bool = True,
) -> bool:
    return bool(
        reactor.state.template.unarmed_opportunity_attack is not None
        and distance_before_ft <= 5 < distance_after_ft
        and _can_react(reactor, mover, movement_source, disengaged=disengaged, can_see=can_see)
    )


def opportunity_attack_available(
    reactor: EncounterCombatant, mover: EncounterCombatant,
    distance_before_ft: int, distance_after_ft: int, movement_source: MovementSource,
    *, disengaged: bool = False, can_see: bool = True,
) -> bool:
    return bool(
        opportunity_attack_weapon(
            reactor, mover, distance_before_ft, distance_after_ft, movement_source,
            disengaged=disengaged, can_see=can_see,
        )
        or unarmed_opportunity_available(
            reactor, mover, distance_before_ft, distance_after_ft, movement_source,
            disengaged=disengaged, can_see=can_see,
        )
    )
