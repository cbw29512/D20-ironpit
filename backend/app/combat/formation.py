from __future__ import annotations

from app.domain.models import CombatantTemplate, WeaponAttackKind

HERO_BACKLINE_FT = 0
HERO_FRONTLINE_FT = 5
MONSTER_FRONTLINE_FT = 10
MONSTER_BACKLINE_FT = 15


def has_ranged_weapon_offense(template: CombatantTemplate) -> bool:
    """Return whether the card has a real ranged weapon attack, not merely a support role."""
    return any(
        attack.weapon.attack_kind is WeaponAttackKind.RANGED
        and attack.weapon.long_range_ft is not None
        and attack.weapon.long_range_ft > 5
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
    )


def has_true_range_offense(template: CombatantTemplate) -> bool:
    """Classify backline starts from actual ranged offense only; buffs never create a backliner."""
    if has_ranged_weapon_offense(template):
        return True
    if any(action.range_ft > 5 for action in template.saving_throw_actions):
        return True
    if any(action.attack_kind == "ranged" and action.range_ft > 5 for action in template.spell_attack_actions):
        return True
    return any(action.range_ft > 5 for action in template.spell_save_actions)


def uses_backline(template: CombatantTemplate) -> bool:
    return has_true_range_offense(template)


def starting_position_ft(template: CombatantTemplate, side: str) -> int:
    backline = uses_backline(template)
    if side == "heroes":
        return HERO_BACKLINE_FT if backline else HERO_FRONTLINE_FT
    if side == "monsters":
        return MONSTER_BACKLINE_FT if backline else MONSTER_FRONTLINE_FT
    raise ValueError(f"Unknown encounter side: {side}")


def backline_holds_position(member, setup) -> bool:
    """Use a real ranged weapon while separated; switch to melee once an active enemy reaches 5 feet."""
    if not has_ranged_weapon_offense(member.state.template):
        return False
    enemies = setup.monsters if member.side == "heroes" else setup.heroes
    return not any(
        enemy.state.is_alive and not enemy.state.is_dead and enemy.state.current_hp > 0
        and abs(member.position_ft - enemy.position_ft) <= 5
        for enemy in enemies
    )
