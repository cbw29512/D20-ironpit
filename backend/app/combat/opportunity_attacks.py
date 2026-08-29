from __future__ import annotations

from typing import Literal

from app.combat.action_economy import is_available, spend
from app.combat.ally_context import pack_tactics_active
from app.combat.attacks import resolve_attack
from app.combat.dice import DiceProvider
from app.combat.policy import weapon_attack_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack, WeaponAttackKind

MovementSource = Literal["speed", "action", "bonus_action", "reaction", "forced", "teleport"]
_PROVOKING_SOURCES = frozenset({"speed", "action", "bonus_action", "reaction"})


def _melee_departure_attack(reactor: EncounterCombatant, before: int, after: int) -> WeaponAttack | None:
    for attack in weapon_attack_profiles(reactor.state):
        weapon = attack.weapon
        if weapon.attack_kind is WeaponAttackKind.MELEE and before <= weapon.reach_ft < after: return attack
    return None


def resolve_opportunity_attack(
    sequence: int, round_number: int, reactor: EncounterCombatant, mover: EncounterCombatant,
    setup: EncounterSetup, distance_before_ft: int, distance_after_ft: int, movement_source: MovementSource,
    dice: DiceProvider, *, disengaged: bool = False, can_see: bool = True,
) -> BattleEvent | None:
    if reactor.side == mover.side or not can_see or disengaged: return None
    if movement_source not in _PROVOKING_SOURCES or not is_available(reactor.state, "reaction"): return None
    attack = _melee_departure_attack(reactor, distance_before_ft, distance_after_ft)
    if attack is None: return None
    spend(reactor.state, "reaction")
    pack = pack_tactics_active(reactor, mover, setup)
    return resolve_attack(
        sequence, round_number, reactor.state, mover.state, attack, distance_before_ft, dice,
        actor_event_id=reactor.combatant_id, target_event_id=mover.combatant_id, spend_action=False,
        advantage_sources=1 if pack else 0, feature_id="opportunity-attack", encounter_setup=setup,
    )
