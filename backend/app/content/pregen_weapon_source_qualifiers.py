from __future__ import annotations

import logging

from app.content.attack_bonus_rules import printed_magic_weapon_attack_damage_bonus
from app.domain.damage_sources import DamageSourceQualifier
from app.domain.models import CombatantTemplate, WeaponAttack

logger = logging.getLogger(__name__)
_UNARMED_WEAPON_IDS = frozenset({"unarmed-strike"})
_SILVERED = [DamageSourceQualifier.SILVERED]
_MAGICAL = [DamageSourceQualifier.MAGICAL]


def canonical_pregen_weapon_source_qualifiers(level: int) -> list[DamageSourceQualifier]:
    """Return the fixed manufactured-weapon qualifiers for one pregen level.

    Levels 1–4: PHB silvered material only (no magic-item table roll).
    Levels 5+: printed Table F/G/H Weapon +N, which is magical and not silvered.
    """
    try:
        if printed_magic_weapon_attack_damage_bonus(level) > 0:
            return list(_MAGICAL)
        if level in range(1, 21):
            return list(_SILVERED)
        raise ValueError("Canonical pregen weapon qualifiers cover levels 1 through 20.")
    except ValueError:
        raise
    except Exception as extra:
        logger.exception("Failed to resolve canonical pregen weapon qualifiers at level %s.", level)
        raise RuntimeError("Canonical pregen weapon source qualifiers could not be resolved.") from extra


def canonical_pregen_weapon_plus_bonus(level: int) -> int:
    """Return the fixed Weapon +N attack and damage bonus for one pregen level."""
    try:
        return printed_magic_weapon_attack_damage_bonus(level)
    except ValueError:
        raise
    except Exception as extra:
        logger.exception("Failed to resolve canonical pregen Weapon +N bonus at level %s.", level)
        raise RuntimeError("Canonical pregen Weapon +N bonus could not be resolved.") from extra


def _is_unarmed(attack: WeaponAttack) -> bool:
    return attack.weapon.id in _UNARMED_WEAPON_IDS or attack.weapon.name.casefold() == "unarmed strike"


def _with_fixed_loadout(attack: WeaponAttack, granted: list[DamageSourceQualifier], plus: int) -> WeaponAttack:
    if _is_unarmed(attack):
        return attack
    already_magical = DamageSourceQualifier.MAGICAL in attack.damage_source_qualifiers
    merged = list(dict.fromkeys([*attack.damage_source_qualifiers, *granted]))
    applied_plus = 0 if already_magical or plus <= 0 else plus
    if merged == list(attack.damage_source_qualifiers) and applied_plus == 0:
        return attack
    return attack.model_copy(update={
        "damage_source_qualifiers": merged,
        "attack_bonus": attack.attack_bonus + applied_plus,
        "damage_bonus": attack.damage_bonus + applied_plus,
    })


def apply_canonical_pregen_weapon_source_qualifiers(template: CombatantTemplate) -> CombatantTemplate:
    """Stamp the fixed DMG/PHB manufactured-weapon ladder onto a certified pregen."""
    try:
        if template.kind != "character" or template.level is None:
            return template
        granted = canonical_pregen_weapon_source_qualifiers(template.level)
        plus = canonical_pregen_weapon_plus_bonus(template.level)
        primary = _with_fixed_loadout(template.weapon_attack, granted, plus)
        alternates = [_with_fixed_loadout(item, granted, plus) for item in template.alternate_weapon_attacks]
        if primary is template.weapon_attack and alternates == list(template.alternate_weapon_attacks):
            return template
        return template.model_copy(update={
            "weapon_attack": primary,
            "alternate_weapon_attacks": alternates,
        })
    except ValueError:
        raise
    except Exception as extra:
        logger.exception("Failed to apply canonical pregen weapon loadout for %s.", template.id)
        raise RuntimeError("Canonical pregen weapon loadout could not be applied.") from extra
