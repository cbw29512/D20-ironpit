"""Standard Iron Pit weapon engagement uses live rows, never display distance.

Schema: EncounterSetup.arena_mode selects grid (legacy fixture) or formation.
State: formation_row and current HP are fight-local; source attack reach and
range stay immutable on the originating card and never determine eligibility
in a standard formation fight.
"""
from __future__ import annotations

import logging

from app.combat.formation import uses_backline
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


def formation_mode(setup: EncounterSetup | None) -> bool:
    try:
        return setup is not None and setup.arena_mode == "formation"
    except Exception:
        logger.exception("Failed to read encounter arena mode.")
        raise


def _active(member: EncounterCombatant) -> bool:
    state = member.state
    return state.is_alive and not state.is_dead and state.current_hp > 0


def effective_row(member: EncounterCombatant, setup: EncounterSetup) -> str:
    """Promotion is immediate even before the normal turn-start row sync."""
    try:
        row = member.state.formation_row
        if row not in {"front", "back"}:
            row = "back" if uses_backline(member.state.template) else "front"
        if row == "front":
            return "front"
        allies = setup.heroes if member.side == "heroes" else setup.monsters
        active_front = any(
            ally.state.formation_row == "front" and _active(ally)
            for ally in allies
        )
        return "back" if active_front else "front"
    except Exception:
        logger.exception("Failed effective formation row for %s.", member.combatant_id)
        raise


def weapon_target_allowed(
    attacker: EncounterCombatant,
    defender: EncounterCombatant,
    attack: WeaponAttack,
    setup: EncounterSetup,
) -> bool:
    """Melee requires an exposed frontline actor and target, not reach in feet."""
    try:
        if not formation_mode(setup):
            return True
        if not _active(defender):
            return False
        if attack.weapon.attack_kind is WeaponAttackKind.MELEE:
            return (
                effective_row(attacker, setup) == "front"
                and effective_row(defender, setup) == "front"
            )
        # Real ranged profiles remain usable. A promoted caster/archer
        # cannot gain a fictional melee profile by switching rows.
        return attack.weapon.attack_kind is WeaponAttackKind.RANGED
    except Exception:
        logger.exception("Failed formation weapon targeting for %s.", attacker.combatant_id)
        raise


def engagement_distance(attack: WeaponAttack) -> int:
    """Roll-pipeline adapter, not a measured or movable arena distance.

    Current dice/condition pipelines accept a distance integer. The legal
    formation attack supplies its own engaged attack context without using
    the 24x16 display positions. Replace this adapter when the shared attack
    roll API gains a typed, non-spatial engagement context.
    """
    try:
        weapon = attack.weapon
        if weapon.attack_kind is WeaponAttackKind.MELEE:
            return min(5, weapon.reach_ft)
        if weapon.normal_range_ft is None or weapon.normal_range_ft <= 0:
            raise ValueError(f"{weapon.name} lacks its printed ranged profile.")
        return weapon.normal_range_ft
    except Exception:
        logger.exception("Failed formation attack context for %s.", attack.id)
        raise
