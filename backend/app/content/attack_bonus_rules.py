from __future__ import annotations

import logging

from app.content.fighting_style_rules import FightingStyleSelection, has_fighting_style
from app.domain.models import WeaponAttackKind

logger = logging.getLogger(__name__)
# Deterministic hoard-band ladder. 2014 DMG Treasure Hoard tables (p.137–138)
# use the same CR 0–4 / 5–10 / 11–16 / 17+ bands as character levels 1–4 / 5–10 /
# 11–16 / 17–20. Magic Item Tables F/G/H (p.144–149) print Weapon +1/+2/+3.
_TABLE_F_FROM_LEVEL = 5
_TABLE_G_FROM_LEVEL = 11
_TABLE_H_FROM_LEVEL = 17


def archery_fighting_style_bonus(
    fighting_styles: FightingStyleSelection,
    weapon_kind: WeaponAttackKind,
) -> int:
    """Return the shared Archery bonus for attacks made with Ranged weapons."""
    try:
        if not isinstance(weapon_kind, WeaponAttackKind):
            raise ValueError("Archery requires a typed weapon attack kind.")
        return 2 if has_fighting_style(fighting_styles, "Archery") and weapon_kind is WeaponAttackKind.RANGED else 0
    except ValueError:
        raise
    except Exception as extra:
        logger.exception("Archery Fighting Style attack compilation failed.")
        raise RuntimeError("Archery Fighting Style attack bonus could not be compiled.") from extra


def printed_magic_weapon_attack_damage_bonus(level: int) -> int:
    """Return the fixed Weapon +N bonus for a pregen level. No random hoard rolls."""
    try:
        if level not in range(1, 21):
            raise ValueError("Printed magic-weapon bonuses cover levels 1 through 20.")
        if level >= _TABLE_H_FROM_LEVEL:
            return 3
        if level >= _TABLE_G_FROM_LEVEL:
            return 2
        if level >= _TABLE_F_FROM_LEVEL:
            return 1
        return 0
    except ValueError:
        raise
    except Exception as extra:
        logger.exception("Printed magic-weapon bonus compilation failed at level %s.", level)
        raise RuntimeError("Printed magic-weapon bonus could not be compiled.") from extra


def compile_weapon_attack_bonus(
    base_attack_bonus: int,
    fighting_styles: FightingStyleSelection,
    weapon_kind: WeaponAttackKind,
) -> int:
    """Compile permanent weapon attack bonuses before combat-time roll modifiers for either ruleset."""
    try:
        return base_attack_bonus + archery_fighting_style_bonus(fighting_styles, weapon_kind)
    except ValueError:
        raise
    except Exception as extra:
        logger.exception("Weapon attack bonus compilation failed.")
        raise RuntimeError("Weapon attack bonus could not be compiled.") from extra
