from __future__ import annotations

from app.domain.combat_treasure import CombatTreasureAward
from app.domain.models import CombatantTemplate, WeaponAttack

_TABLE = {
    1: "defense", 2: "saving-throws", 3: "max-hp", 4: "initiative", 5: "speed",
    6: "resource", 7: "focus", 8: "offense", 9: "defense", 10: "resource",
    11: "offense", 12: "focus", 13: "saving-throws", 14: "max-hp", 15: "initiative",
    16: "speed", 17: "resource", 18: "defense", 19: "focus", 20: "offense",
}


def treasure_bonus(level: int) -> int:
    if not 2 <= level <= 20:
        raise ValueError("Combat treasure levels must be between 2 and 20.")
    return 1 if level <= 8 else 2 if level <= 16 else 3


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


def _resource_id(template: CombatantTemplate) -> str | None:
    return next((item.id for item in template.resources if not item.id.startswith("spell-slot-")), None)


def _offense(template: CombatantTemplate, level: int, chance: int, table: int) -> CombatTreasureAward:
    bonus = treasure_bonus(level)
    if _spellcaster(template) and not template.weapon_masteries and template.attack_action is None:
        return CombatTreasureAward(
            level=level, chance_roll=chance, table_roll=table, slot="focus", effect="spell-focus",
            name=f"Combat Focus +{bonus}", bonus=bonus,
        )
    attack = _preferred_weapon(template)
    return CombatTreasureAward(
        level=level, chance_roll=chance, table_roll=table, slot="offense", effect="weapon-enhancement",
        name=f"{attack.weapon.name} +{bonus}", bonus=bonus, target_id=attack.id,
    )


def resolve_combat_treasure(
    template: CombatantTemplate, level: int, chance_roll: int, table_roll: int,
) -> CombatTreasureAward | None:
    """51-100 awards treasure; d20 11 is the canonical primary-offense result."""
    if not 1 <= chance_roll <= 100 or not 1 <= table_roll <= 20:
        raise ValueError("Treasure rolls require d100=1..100 and d20=1..20.")
    if chance_roll <= 50:
        return None
    family = _TABLE[table_roll]
    bonus = treasure_bonus(level)
    if family == "offense":
        return _offense(template, level, chance_roll, table_roll)
    if family == "focus":
        return _offense(template, level, chance_roll, table_roll) if not _spellcaster(template) else CombatTreasureAward(
            level=level, chance_roll=chance_roll, table_roll=table_roll, slot="focus", effect="spell-focus",
            name=f"Combat Focus +{bonus}", bonus=bonus,
        )
    if family == "resource":
        resource_id = _resource_id(template)
        if resource_id is None:
            family = "defense"
        else:
            return CombatTreasureAward(
                level=level, chance_roll=chance_roll, table_roll=table_roll, slot="resource",
                effect="resource-use", name=f"{resource_id.replace('-', ' ').title()} Talisman +{bonus}",
                bonus=bonus, target_id=resource_id,
            )
    effect = {
        "defense": ("defense", "armor-class", f"Defensive Ward +{bonus}"),
        "saving-throws": ("accessory", "saving-throws", f"Protection Charm +{bonus}"),
        "initiative": ("accessory", "initiative", f"Initiative Charm +{bonus}"),
        "speed": ("accessory", "speed", f"Speed Charm +{bonus}"),
        "max-hp": ("accessory", "max-hp", f"Vitality Charm +{bonus}"),
    }[family]
    return CombatTreasureAward(
        level=level, chance_roll=chance_roll, table_roll=table_roll,
        slot=effect[0], effect=effect[1], name=effect[2], bonus=bonus,
    )
