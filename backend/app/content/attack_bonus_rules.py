from __future__ import annotations

import logging

from app.domain.models import WeaponAttackKind

logger = logging.getLogger(__name__)


def archery_fighting_style_bonus(
    fighting_style: str | None,
    weapon_kind: WeaponAttackKind,
) -> int:
    """Return the static 2024 Archery bonus for attacks made with Ranged weapons."""
    try:
        if not isinstance(weapon_kind, WeaponAttackKind):
            raise ValueError("Archery requires a typed weapon attack kind.")
        return 2 if fighting_style == "Archery" and weapon_kind is WeaponAttackKind.RANGED else 0
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Archery Fighting Style attack compilation failed.")
        raise RuntimeError("Archery Fighting Style attack bonus could not be compiled.") from exc


def compile_weapon_attack_bonus(
    base_attack_bonus: int,
    fighting_style: str | None,
    weapon_kind: WeaponAttackKind,
) -> int:
    """Compile permanent weapon attack bonuses before combat-time roll modifiers."""
    try:
        return base_attack_bonus + archery_fighting_style_bonus(fighting_style, weapon_kind)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Weapon attack bonus compilation failed.")
        raise RuntimeError("Weapon attack bonus could not be compiled.") from exc
