from __future__ import annotations

import logging

from app.combat.formation import has_ranged_weapon_offense, uses_backline
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import CombatantTemplate, WeaponAttackKind

logger = logging.getLogger(__name__)


def _alive(member: EncounterCombatant) -> bool:
    state = member.state
    return state.is_alive and not state.is_dead and state.current_hp > 0


def has_melee_weapon(template: CombatantTemplate) -> bool:
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    return any(attack.weapon.attack_kind is WeaponAttackKind.MELEE for attack in attacks)


def has_ranged_or_spell_offense(template: CombatantTemplate) -> bool:
    return uses_backline(template) or has_ranged_weapon_offense(template)


def assign_formation_rows(members: list[EncounterCombatant]) -> None:
    """Fill up to three front and three back starting slots, preferring melee offense."""
    try:
        if len(members) > 6:
            raise ValueError("Iron Pit supports at most six combatants per side.")

        def front_priority(member: EncounterCombatant) -> int:
            template = member.state.template
            if uses_backline(template):
                return 2
            return 1 if has_ranged_weapon_offense(template) and has_melee_weapon(template) else 0

        ranked = sorted(range(len(members)), key=lambda i: (front_priority(members[i]), i))
        front_indices = {i for i in ranked if front_priority(members[i]) < 2}
        front_indices = set(sorted(front_indices, key=lambda i: (front_priority(members[i]), i))[:3])
        back_indices = {i for i in ranked if i not in front_indices and front_priority(members[i]) == 2}
        back_indices = set(sorted(back_indices)[:3])
        # Spill over only when one preferred row is full: six all-ranged or six
        # all-melee must fit the same three-by-two deployment without exceptions.
        for index in ranked:
            if index in front_indices or index in back_indices:
                continue
            if len(front_indices) < 3:
                front_indices.add(index)
            else:
                back_indices.add(index)
        for index, member in enumerate(members):
            row = "front" if index in front_indices else "back"
            member.state.formation_row = row
            member.state.initial_formation_row = row
    except Exception:
        logger.exception("Failed to assign formation rows.")
        raise


def member_is_backline(member: EncounterCombatant) -> bool:
    row = member.state.formation_row
    if row == "front":
        return False
    if row == "back":
        return True
    return uses_backline(member.state.template)


def _living_frontline(allies: list[EncounterCombatant], current: EncounterCombatant) -> bool:
    return any(
        ally.combatant_id != current.combatant_id
        and _alive(ally)
        and ally.state.formation_row == "front"
        for ally in allies
    )


def sync_formation_rows(setup: EncounterSetup) -> list[EncounterCombatant]:
    """Promote every surviving backliner once its side loses the entire frontline."""
    try:
        promoted: list[EncounterCombatant] = []
        for side in (setup.heroes, setup.monsters):
            for member in side:
                if not _alive(member) or member.state.formation_row != "back":
                    continue
                if _living_frontline(side, member):
                    continue
                member.state.formation_row = "front"
                promoted.append(member)
        return promoted
    except Exception:
        logger.exception("Failed to sync formation rows.")
        raise
