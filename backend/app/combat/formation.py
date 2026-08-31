from __future__ import annotations

from app.combat.condition_rules import is_incapacitated
from app.domain.models import CombatantTemplate, WeaponAttackKind

HERO_BACKLINE_FT = 0
HERO_FRONTLINE_FT = 5
MONSTER_FRONTLINE_FT = 10
MONSTER_BACKLINE_FT = 15


def uses_backline(template: CombatantTemplate) -> bool:
    """Put dedicated ranged characters/casters in back; primary-melee combatants start engaged in front."""
    if template.weapon_attack.weapon.attack_kind is WeaponAttackKind.RANGED:
        return True
    if template.kind == "character" and (template.spell_save_actions or template.defensive_spell_actions):
        return True
    return False


def starting_position_ft(template: CombatantTemplate, side: str) -> int:
    backline = uses_backline(template)
    if side == "heroes":
        return HERO_BACKLINE_FT if backline else HERO_FRONTLINE_FT
    if side == "monsters":
        return MONSTER_BACKLINE_FT if backline else MONSTER_FRONTLINE_FT
    raise ValueError(f"Unknown encounter side: {side}")


def backline_holds_position(member, setup) -> bool:
    """Arena policy: dedicated backliners stay behind an active allied frontline."""
    if not uses_backline(member.state.template):
        return False
    allies = setup.heroes if member.side == "heroes" else setup.monsters
    return any(
        ally.combatant_id != member.combatant_id
        and not uses_backline(ally.state.template)
        and ally.state.is_alive
        and not ally.state.is_dead
        and ally.state.current_hp > 0
        and not is_incapacitated(ally.state)
        for ally in allies
    )
