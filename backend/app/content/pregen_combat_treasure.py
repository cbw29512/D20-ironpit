from __future__ import annotations

import hashlib

from app.domain.combat_treasure import CombatTreasureAward
from app.domain.models import CombatantTemplate, WeaponAttack


def treasure_bonus(level: int) -> int:
    """Iron Pit treasure power: +1/+2/+3/+4/+5 across five level bands."""
    if not 2 <= level <= 20:
        raise ValueError("Combat treasure levels must be between 2 and 20.")
    if level <= 4:
        return 1
    if level <= 8:
        return 2
    if level <= 12:
        return 3
    if level <= 16:
        return 4
    return 5


def canonical_treasure_roll(ruleset: str, class_id: str, build_id: str, level: int) -> int:
    """Stable d100: random-looking once, reproducible forever for CI and replay."""
    if not 2 <= level <= 20:
        raise ValueError("Combat treasure levels must be between 2 and 20.")
    key = f"{ruleset}:{class_id}:{build_id}:{level}:iron-pit-treasure-v1".encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big") % 100 + 1


def _attacks(template: CombatantTemplate) -> list[WeaponAttack]:
    return [template.weapon_attack, *template.alternate_weapon_attacks]


def _preferred_weapon(template: CombatantTemplate) -> WeaponAttack:
    attacks = _attacks(template)
    for mastery in template.weapon_masteries:
        match = next((attack for attack in attacks if attack.weapon.id == mastery), None)
        if match is not None:
            return match
    return template.weapon_attack


def _spellcaster(template: CombatantTemplate) -> bool:
    return bool(template.spell_attack_actions or template.spell_save_actions or template.defensive_spell_actions)


def _offense(template: CombatantTemplate, level: int, roll: int) -> CombatTreasureAward:
    bonus = treasure_bonus(level)
    if _spellcaster(template) and not template.weapon_masteries and template.attack_action is None:
        return CombatTreasureAward(
            level=level, roll=roll, slot="offense", effect="spell-focus",
            name=f"Combat Focus +{bonus}", bonus=bonus,
        )
    attack = _preferred_weapon(template)
    return CombatTreasureAward(
        level=level, roll=roll, slot="offense", effect="weapon-enhancement",
        name=f"{attack.weapon.name} +{bonus}", bonus=bonus, target_id=attack.id,
    )


def _armor(template: CombatantTemplate, level: int, roll: int) -> CombatTreasureAward:
    bonus = treasure_bonus(level)
    armor_name = template.visual.armor.replace("-", " ").title()
    if armor_name.casefold() in {"none", "unarmored", "natural"}:
        armor_name = "Bracers of Defense"
    else:
        armor_name = f"{armor_name} +{bonus}"
    return CombatTreasureAward(
        level=level, roll=roll, slot="defense", effect="armor-class",
        name=armor_name, bonus=bonus,
    )


def _potion(level: int, roll: int) -> CombatTreasureAward:
    bonus = treasure_bonus(level)
    return CombatTreasureAward(
        level=level, roll=roll, slot="consumable", effect="healing-potion",
        name=f"Combat Healing Potion Tier {bonus}", bonus=bonus,
    )


def _accessory(level: int, roll: int) -> CombatTreasureAward:
    bonus = treasure_bonus(level)
    variants = {
        91: ("saving-throws", f"Helm of Protection +{bonus}"),
        92: ("initiative", f"Boots of Readiness +{bonus}"),
        93: ("speed", f"Boots of Speed +{bonus}"),
        94: ("max-hp", f"Amulet of Vitality +{bonus}"),
        95: ("saving-throws", f"Cloak of Protection +{bonus}"),
        96: ("initiative", f"Helm of Awareness +{bonus}"),
        97: ("speed", f"Greaves of Quickness +{bonus}"),
        98: ("max-hp", f"Belt of Fortitude +{bonus}"),
        99: ("saving-throws", f"Ring of Protection +{bonus}"),
    }
    effect, name = variants[roll]
    return CombatTreasureAward(
        level=level, roll=roll, slot="accessory", effect=effect,
        name=name, bonus=bonus,
    )


def resolve_combat_treasure(
    template: CombatantTemplate,
    level: int,
    roll: int,
) -> list[CombatTreasureAward]:
    """One-roll table: 1-50 none; 100 guarantees two different useful items."""
    if not 1 <= roll <= 100:
        raise ValueError("Combat treasure roll must be between 1 and 100.")
    if roll <= 50:
        return []
    if roll <= 60:
        return [_armor(template, level, roll)]
    if roll <= 70:
        return [_offense(template, level, roll)]
    if roll <= 80:
        return [_potion(level, roll)]
    if roll <= 90:
        return [_armor(template, level, roll)]
    if roll <= 99:
        return [_accessory(level, roll)]
    return [_offense(template, level, roll), _armor(template, level, roll)]
