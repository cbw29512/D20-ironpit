from __future__ import annotations

from dataclasses import dataclass

from app.content.armor_class_rules import compile_armored_base_ac


@dataclass(frozen=True)
class FighterCombatLevel:
    level: int
    proficiency_bonus: int
    armor_class: int
    max_hp: int
    strength: int
    dexterity: int
    constitution: int
    attack_count: int
    weapon_masteries: tuple[str, ...]
    second_wind_uses: int
    action_surge_uses: int
    indomitable_uses: int
    features_added: tuple[str, ...] = ()
    features_removed: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()
    source: str = ""


_M3 = ("flail", "javelin", "spear")
_M4 = (*_M3, "longsword")
_M4_GS = (*_M3, "greatsword")
_M5 = (*_M4_GS, "shortbow")
_M6 = (*_M5, "longsword")
_DEFENSE_AC = compile_armored_base_ac(16, "Defense", "heavy")


def _r(level: int, pb: int, hp: int, strength: int, dexterity: int, constitution: int,
       attacks: int, masteries: tuple[str, ...], second_wind: int, action_surge: int,
       indomitable: int, *, add: tuple[str, ...] = (), remove: tuple[str, ...] = (),
       ignored: tuple[str, ...] = (), source: str = "") -> FighterCombatLevel:
    return FighterCombatLevel(level, pb, _DEFENSE_AC, hp, strength, dexterity, constitution, attacks,
                              masteries, second_wind, action_surge, indomitable, add, remove,
                              ignored, source)


FIGHTER_COMBAT_LEVELS: dict[int, FighterCombatLevel] = {
    1: _r(1, 2, 12, 17, 13, 15, 1, _M3, 2, 0, 0, add=("second-wind", "savage-attacker", "adrenaline-rush", "relentless-endurance"), source="D&D Beyond Basic Rules 2024: Fighter, Orc, Soldier, Savage Attacker, Equipment"),
    2: _r(2, 2, 20, 17, 13, 15, 1, _M3, 2, 1, 0, add=("action-surge", "tactical-mind"), source="D&D Beyond Basic Rules 2024: Fighter 2, Orc, Soldier, Savage Attacker, Equipment"),
    3: _r(3, 2, 28, 17, 13, 15, 1, _M3, 2, 1, 0, add=("improved-critical", "remarkable-athlete"), source="D&D Beyond Basic Rules 2024: Fighter 3 Champion, Orc, Soldier, Savage Attacker, Equipment"),
    4: _r(4, 2, 40, 18, 13, 16, 1, _M4, 3, 1, 0, source="D&D Beyond Basic Rules 2024: Fighter 4 Ability Score Improvement, Second Wind, Weapon Mastery, Champion, Orc, Soldier, Savage Attacker, Equipment"),
    5: _r(5, 3, 49, 18, 13, 16, 2, _M4, 3, 1, 0, add=("extra-attack", "tactical-shift"), source="D&D Beyond Basic Rules 2024: Fighter 5 Extra Attack and Tactical Shift, Champion, Orc, Soldier, Savage Attacker, Equipment"),
    6: _r(6, 3, 58, 20, 13, 16, 2, _M4, 3, 1, 0, source="D&D Beyond Basic Rules 2024: Fighter 6 Ability Score Improvement, Champion, Orc, Soldier, Savage Attacker, Equipment"),
    7: _r(7, 3, 67, 20, 13, 16, 2, _M4, 3, 1, 0, add=("great-weapon-fighting",), source="D&D Beyond Basic Rules 2024: Fighter 7 Champion Additional Fighting Style, Great Weapon Fighting, Orc, Soldier, Savage Attacker, Equipment"),
    8: _r(8, 3, 84, 20, 13, 18, 2, _M4, 3, 1, 0, source="D&D Beyond Basic Rules 2024: Fighter 8 Ability Score Improvement, Champion, Great Weapon Fighting, Orc, Soldier, Savage Attacker, Equipment"),
    9: _r(9, 4, 94, 20, 13, 18, 2, _M4_GS, 3, 1, 1, add=("indomitable", "tactical-master"), ignored=("tactical-master-push", "tactical-master-slow"), source="D&D Beyond Basic Rules 2024: Fighter 9 Indomitable and Tactical Master, Champion, Great Weapon Fighting, Orc, Soldier, Savage Attacker, Equipment"),
    10: _r(10, 4, 104, 20, 13, 18, 2, _M5, 4, 1, 1, add=("heroic-warrior",), source="D&D Beyond Basic Rules 2024: Fighter 10 Champion Heroic Warrior"),
    11: _r(11, 4, 114, 20, 13, 18, 3, _M5, 4, 1, 1, source="D&D Beyond Basic Rules 2024: Fighter 11 Two Extra Attacks"),
    12: _r(12, 4, 136, 20, 13, 20, 3, _M5, 4, 1, 1, source="D&D Beyond Basic Rules 2024: Fighter 12 Ability Score Improvement (+2 Constitution)"),
    13: _r(13, 5, 147, 20, 13, 20, 3, _M5, 4, 1, 2, add=("studied-attacks",), source="D&D Beyond Basic Rules 2024: Fighter 13 Indomitable and Studied Attacks"),
    14: _r(14, 5, 158, 20, 15, 20, 3, _M5, 4, 1, 2, source="D&D Beyond Basic Rules 2024: Fighter 14 Ability Score Improvement (+2 Dexterity)"),
    15: _r(15, 5, 169, 20, 15, 20, 3, _M5, 4, 1, 2, add=("superior-critical",), remove=("improved-critical",), source="D&D Beyond Basic Rules 2024: Fighter 15 Champion Superior Critical"),
    16: _r(16, 5, 180, 20, 17, 20, 3, _M6, 4, 1, 2, source="D&D Beyond Basic Rules 2024: Fighter 16 Ability Score Improvement (+2 Dexterity)"),
    17: _r(17, 6, 191, 20, 17, 20, 3, _M6, 4, 2, 3, source="D&D Beyond Basic Rules 2024: Fighter 17 Action Surge and Indomitable uses increase"),
    18: _r(18, 6, 202, 20, 17, 20, 3, _M6, 4, 2, 3, add=("survivor-defy-death", "survivor-heroic-rally"), source="D&D Beyond Basic Rules 2024: Fighter 18 Champion Survivor"),
    19: _r(19, 6, 213, 20, 18, 20, 3, _M6, 4, 2, 3, add=("boon-combat-prowess",), source="D&D Beyond Basic Rules 2024: Fighter 19 Boon of Combat Prowess (+1 Dexterity)"),
    20: _r(20, 6, 224, 20, 18, 20, 4, _M6, 4, 2, 3, source="D&D Beyond Basic Rules 2024: Fighter 20 Three Extra Attacks"),
}


def fighter_combat_features(level: int) -> tuple[str, ...]:
    if level not in FIGHTER_COMBAT_LEVELS:
        raise ValueError(f"Fighter level {level} must be between 1 and 20.")
    active: list[str] = []
    for current in range(1, level + 1):
        row = FIGHTER_COMBAT_LEVELS[current]
        active = [feature for feature in active if feature not in row.features_removed]
        active.extend(feature for feature in row.features_added if feature not in active)
    return tuple(active)


def fighter_arena_ignored(level: int) -> tuple[str, ...]:
    ignored: list[str] = []
    for current in range(1, level + 1):
        ignored.extend(item for item in FIGHTER_COMBAT_LEVELS[current].arena_ignored if item not in ignored)
    return tuple(ignored)
