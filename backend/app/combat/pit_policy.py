from __future__ import annotations

import logging

from app.combat.attack_legality import attack_allowed_against
from app.combat.encounter_targeting import combatant_distance, living_opponents
from app.combat.formation import uses_backline
from app.combat.range import resolve_attack_roll_mode
from app.combat.resources import resource_available
from app.combat.swallow_policy import forbidden_attacks_while_swallowing
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def is_backline(member: EncounterCombatant) -> bool:
    return uses_backline(member.state.template)


def target_order(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    *,
    prefer_backline: bool = False,
) -> list[EncounterCombatant]:
    """Return active Pit targets by formation role without using movement distance as priority."""
    opponents = living_opponents(attacker, setup)
    front = [target for target in opponents if not is_backline(target)]
    back = [target for target in opponents if is_backline(target)]
    return [*back, *front] if prefer_backline else [*front, *back]


def has_frontline_target(attacker: EncounterCombatant, setup: EncounterSetup) -> bool:
    return any(not is_backline(target) for target in living_opponents(attacker, setup))


def has_backline_target(attacker: EncounterCombatant, setup: EncounterSetup) -> bool:
    return any(is_backline(target) for target in living_opponents(attacker, setup))


def allied_frontline_active(attacker: EncounterCombatant, setup: EncounterSetup) -> bool:
    allies = setup.heroes if attacker.side == "heroes" else setup.monsters
    return any(
        ally.combatant_id != attacker.combatant_id
        and ally.state.is_alive
        and not ally.state.is_dead
        and ally.state.current_hp > 0
        and not is_backline(ally)
        for ally in allies
    )


def attack_distance(attacker: EncounterCombatant, target: EncounterCombatant, attack: WeaponAttack) -> int:
    """Return authoritative battlefield distance; range legality belongs to the shared range resolver."""
    try:
        return combatant_distance(attacker, target)
    except Exception as exc:
        logger.exception("Failed to read attack distance for %s using %s.", attacker.combatant_id, attack.id)
        raise RuntimeError("Attack distance could not be evaluated.") from exc


def save_distance(attacker: EncounterCombatant, target: EncounterCombatant, range_ft: int) -> int:
    try:
        if range_ft < 0:
            raise ValueError("Save-action range cannot be negative.")
        return combatant_distance(attacker, target)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to read save-action distance for %s.", attacker.combatant_id)
        raise RuntimeError("Save-action distance could not be evaluated.") from exc


def _attack_profiles(attacker: EncounterCombatant, allowed_ids: list[str], kind: WeaponAttackKind | None):
    try:
        allowed = set(allowed_ids)
        return [
            attack
            for attack in [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
            if attack.id in allowed
            and (kind is None or attack.weapon.attack_kind is kind)
            and resource_available(attacker.state, attack.resource_id, attack.resource_cost)
        ]
    except Exception as exc:
        logger.exception("Failed to collect legal resource attack profiles for %s.", attacker.combatant_id)
        raise RuntimeError("Resource attack profiles could not be evaluated.") from exc


def _attack_in_range(attack: WeaponAttack, distance_ft: int) -> bool:
    try:
        resolve_attack_roll_mode(attack.weapon, distance_ft, close_enemy_active=False)
        return True
    except ValueError:
        return False
    except Exception:
        logger.exception("Failed to evaluate grid range for attack %s.", attack.id)
        raise


def choose_attack(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    allowed_ids: list[str],
    *,
    kind: WeaponAttackKind | None = None,
    prefer_backline: bool = False,
) -> tuple[EncounterCombatant, WeaponAttack, int] | None:
    """Choose an actually legal attack at the combatants' current battlefield positions."""
    try:
        forbidden = forbidden_attacks_while_swallowing(attacker, setup)
        profiles = [attack for attack in _attack_profiles(attacker, allowed_ids, kind) if attack.id not in forbidden]
        for target in target_order(attacker, setup, prefer_backline=prefer_backline):
            distance = combatant_distance(attacker, target)
            for attack in profiles:
                if attack_allowed_against(attack, attacker.combatant_id, target.state) and _attack_in_range(attack, distance):
                    return target, attack, distance
        return None
    except Exception as exc:
        logger.exception("Pit attack selection failed for %s.", attacker.combatant_id)
        raise RuntimeError("Pit attack selection could not be evaluated.") from exc


def choose_standard_attack(
    attacker: EncounterCombatant,
    setup: EncounterSetup,
) -> tuple[EncounterCombatant, WeaponAttack, int] | None:
    """Use legal range now: ranged holds position; melee is preferred when engaged."""
    ids = [
        attacker.state.template.weapon_attack.id,
        *(attack.id for attack in attacker.state.template.alternate_weapon_attacks),
    ]
    if is_backline(attacker) and allied_frontline_active(attacker, setup):
        ranged = choose_attack(attacker, setup, ids, kind=WeaponAttackKind.RANGED)
        if ranged is not None:
            return ranged
    melee = choose_attack(attacker, setup, ids, kind=WeaponAttackKind.MELEE)
    if melee is not None:
        return melee
    return choose_attack(attacker, setup, ids, kind=WeaponAttackKind.RANGED)


def flexible_slot_has_both(attacker: EncounterCombatant, allowed_ids: list[str]) -> bool:
    profiles = _attack_profiles(attacker, allowed_ids, None)
    kinds = {attack.weapon.attack_kind for attack in profiles}
    return WeaponAttackKind.MELEE in kinds and WeaponAttackKind.RANGED in kinds