from __future__ import annotations

import logging

from app.domain.damage_sources import DamageSourceQualifier
from app.domain.models import CombatantTemplate, WeaponAttack

logger = logging.getLogger(__name__)
_UNARMED_WEAPON_IDS = frozenset({"unarmed-strike"})
# 2014 DMG Magic Item Rarity p.135: Common and Uncommon = 1st or higher.
_UNCOMMON_FROM_LEVEL = 1
_DMG_TIER_MANUFACTURED = (
    DamageSourceQualifier.SILVERED,
    DamageSourceQualifier.ADAMANTINE,
    DamageSourceQualifier.MAGICAL,
)


def canonical_pregen_weapon_source_qualifiers(level: int) -> list[DamageSourceQualifier]:
    """Return DMG-table manufactured-weapon source qualifiers for one pregen level.

    Cited tables, not the 1-2/3-4/5+ example band:
    - 2014 DMG Magic Item Rarity (p.135): Uncommon is appropriate at 1st or higher.
      Weapon +1 and adamantine armaments are Uncommon.
    - 2024 DMG Magic Items Awarded by Level and Random Magic Item Rarity: Uncommon
      items are awarded in the 1-4 tier.
    - PHB silvered weapons are special materials, not magic items, so they are
      legal from 1st as well.
    """
    try:
        if level not in range(1, 21):
            raise ValueError("Canonical pregen weapon qualifiers cover levels 1 through 20.")
        if level >= _UNCOMMON_FROM_LEVEL:
            return list(_DMG_TIER_MANUFACTURED)
        return []
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve canonical pregen weapon qualifiers at level %s.", level)
        raise RuntimeError("Canonical pregen weapon source qualifiers could not be resolved.") from exc


def _is_unarmed(attack: WeaponAttack) -> bool:
    return attack.weapon.id in _UNARMED_WEAPON_IDS or attack.weapon.name.casefold() == "unarmed strike"


def _with_loadout_qualifiers(attack: WeaponAttack, granted: list[DamageSourceQualifier]) -> WeaponAttack:
    if _is_unarmed(attack) or not granted:
        return attack
    merged = list(dict.fromkeys([*attack.damage_source_qualifiers, *granted]))
    if merged == list(attack.damage_source_qualifiers):
        return attack
    return attack.model_copy(update={"damage_source_qualifiers": merged})


def apply_canonical_pregen_weapon_source_qualifiers(template: CombatantTemplate) -> CombatantTemplate:
    """Stamp manufactured-weapon source qualifiers onto a certified canonical pregen."""
    try:
        if template.kind != "character" or template.level is None:
            return template
        granted = canonical_pregen_weapon_source_qualifiers(template.level)
        primary = _with_loadout_qualifiers(template.weapon_attack, granted)
        alternates = [_with_loadout_qualifiers(item, granted) for item in template.alternate_weapon_attacks]
        if primary is template.weapon_attack and alternates == list(template.alternate_weapon_attacks):
            return template
        return template.model_copy(update={
            "weapon_attack": primary,
            "alternate_weapon_attacks": alternates,
        })
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply canonical pregen weapon qualifiers for %s.", template.id)
        raise RuntimeError("Canonical pregen weapon source qualifiers could not be applied.") from exc
