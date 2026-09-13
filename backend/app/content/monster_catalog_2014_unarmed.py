from __future__ import annotations

from fractions import Fraction

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.domain.weapons import DamageType, Weapon, WeaponAttack, WeaponAttackKind


def proficiency_bonus_2014(challenge_rating: str | None) -> int:
    """Return the 2014 monster proficiency bonus implied by challenge rating."""
    if challenge_rating is None:
        raise ValueError("2014 Unarmed Strike fallback requires a challenge rating.")
    rating = Fraction(challenge_rating)
    if rating < 0 or rating > 30:
        raise ValueError(f"Unsupported 2014 challenge rating {challenge_rating!r}.")
    if rating <= 4: return 2
    if rating <= 8: return 3
    if rating <= 12: return 4
    if rating <= 16: return 5
    if rating <= 20: return 6
    if rating <= 24: return 7
    if rating <= 28: return 8
    return 9


def unarmed_strike_2014(source: CatalogMonster2014) -> WeaponAttack:
    """Build the universal 2014 Unarmed Strike available to every creature."""
    strength_modifier = (source.abilities["str"] - 10) // 2
    damage = max(0, 1 + strength_modifier)
    weapon = Weapon(
        id="unarmed-strike", name="Unarmed Strike", attack_kind=WeaponAttackKind.MELEE,
        dice_count=0, dice_size=6, damage_type=DamageType.BLUDGEONING,
        animation="melee", reach_ft=5,
    )
    return WeaponAttack(
        id="unarmed-strike", weapon=weapon,
        attack_bonus=strength_modifier + proficiency_bonus_2014(source.challenge_rating),
        damage_bonus=strength_modifier, attack_ability="strength",
        attack_ability_modifier=strength_modifier, fixed_damage=damage,
    )


def attacks_with_unarmed_fallback_2014(
    source: CatalogMonster2014, attacks: list[WeaponAttack],
) -> list[WeaponAttack]:
    return attacks if attacks else [unarmed_strike_2014(source)]
