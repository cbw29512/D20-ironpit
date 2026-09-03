from __future__ import annotations

from app.domain.models import CombatantTemplate, WeaponAttackKind

HERO_BACKLINE_FT = 0
HERO_FRONTLINE_FT = 5
MONSTER_FRONTLINE_FT = 10
MONSTER_BACKLINE_FT = 15


def has_ranged_weapon_offense(template: CombatantTemplate) -> bool:
    """Return whether the card owns any real ranged weapon attack."""
    return any(
        attack.weapon.attack_kind is WeaponAttackKind.RANGED
        and attack.weapon.long_range_ft is not None
        and attack.weapon.long_range_ft > 5
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
    )


def _primary_weapon_is_ranged(template: CombatantTemplate) -> bool:
    weapon = template.weapon_attack.weapon
    return (
        weapon.attack_kind is WeaponAttackKind.RANGED
        and weapon.long_range_ft is not None
        and weapon.long_range_ft > 5
    )


def _has_ranged_spell_offense(template: CombatantTemplate) -> bool:
    if any(action.attack_kind == "ranged" and action.range_ft > 5 for action in template.spell_attack_actions):
        return True
    return any(action.range_ft > 5 for action in template.spell_save_actions)


def has_true_range_offense(template: CombatantTemplate) -> bool:
    """Return whether some supported attack/spell can deal damage beyond melee reach."""
    return has_ranged_weapon_offense(template) or _has_ranged_spell_offense(template)


def uses_backline(template: CombatantTemplate) -> bool:
    """Start back only when ranged combat is the primary plan; backup thrown/ranged attacks do not define formation."""
    return _primary_weapon_is_ranged(template) or _has_ranged_spell_offense(template)


def starting_position_ft(template: CombatantTemplate, side: str) -> int:
    backline = uses_backline(template)
    if side == "heroes":
        return HERO_BACKLINE_FT if backline else HERO_FRONTLINE_FT
    if side == "monsters":
        return MONSTER_BACKLINE_FT if backline else MONSTER_FRONTLINE_FT
    raise ValueError(f"Unknown encounter side: {side}")


def backline_holds_position(member, setup) -> bool:
    """Use a legal ranged weapon while separated; switch to melee once an active enemy reaches 5 feet."""
    if not has_ranged_weapon_offense(member.state.template):
        return False
    enemies = setup.monsters if member.side == "heroes" else setup.heroes
    return not any(
        enemy.state.is_alive and not enemy.state.is_dead and enemy.state.current_hp > 0
        and abs(member.position_ft - enemy.position_ft) <= 5
        for enemy in enemies
    )
