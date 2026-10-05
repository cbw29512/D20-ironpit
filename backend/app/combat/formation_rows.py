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
    """Assign Pit front/back rows from weapons and spells, never creature names."""
    try:
        mixed: list[EncounterCombatant] = []
        for member in members:
            template = member.state.template
            if uses_backline(template):
                member.state.formation_row = "back"
            elif has_ranged_weapon_offense(template) and has_melee_weapon(template):
                mixed.append(member)
            else:
                member.state.formation_row = "front"
        for index, member in enumerate(mixed):
            member.state.formation_row = "front" if index == 0 else "back"
        for member in members:
            member.state.initial_formation_row = member.state.formation_row
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
    """Promote back-row melee-only combatants after the last front-row ally dies."""
    try:
        promoted: list[EncounterCombatant] = []
        for side in (setup.heroes, setup.monsters):
            for member in side:
                if not _alive(member) or member.state.formation_row != "back":
                    continue
                if has_ranged_or_spell_offense(member.state.template):
                    continue
                if _living_frontline(side, member):
                    continue
                member.state.formation_row = "front"
                promoted.append(member)
        return promoted
    except Exception:
        logger.exception("Failed to sync formation rows.")
        raise
