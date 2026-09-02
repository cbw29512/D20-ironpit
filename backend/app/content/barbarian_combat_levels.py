from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BarbarianCombatLevel:
    level: int
    proficiency_bonus: int
    armor_class: int
    max_hp: int
    strength: int
    dexterity: int
    constitution: int
    speed_ft: int
    attack_count: int
    rage_uses: int
    rage_damage_bonus: int
    weapon_masteries: tuple[str, ...]
    features_added: tuple[str, ...] = ()
    features_removed: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()
    source: str = ""


_M2 = ("flail", "pike")
_M3 = (*_M2, "longsword")
_M4 = (*_M3, "greatsword")


def _r(level: int, pb: int, ac: int, hp: int, strength: int, constitution: int,
       speed: int, attacks: int, rages: int, rage_damage: int, masteries: tuple[str, ...],
       *, add: tuple[str, ...] = (), remove: tuple[str, ...] = (), ignored: tuple[str, ...] = (),
       source: str = "") -> BarbarianCombatLevel:
    return BarbarianCombatLevel(level, pb, ac, hp, strength, 13, constitution, speed, attacks,
                                rages, rage_damage, masteries, add, remove, ignored, source)


BARBARIAN_COMBAT_LEVELS: dict[int, BarbarianCombatLevel] = {
    1: _r(1, 2, 13, 14, 17, 15, 30, 1, 2, 2, _M2, add=("rage", "savage-attacker", "adrenaline-rush", "relentless-endurance"), source="D&D Beyond Basic Rules 2024: Barbarian, Orc, Soldier, Savage Attacker, Equipment"),
    2: _r(2, 2, 13, 23, 17, 15, 30, 1, 2, 2, _M2, add=("danger-sense", "reckless-attack"), source="D&D Beyond Basic Rules 2024: Barbarian 2, Orc, Soldier, Savage Attacker, Equipment"),
    3: _r(3, 2, 13, 32, 17, 15, 30, 1, 3, 2, _M2, add=("frenzy",), ignored=("primal-knowledge",), source="D&D Beyond Basic Rules 2024: Barbarian 3 Path of the Berserker, Orc, Soldier, Savage Attacker, Equipment"),
    4: _r(4, 2, 14, 45, 18, 16, 30, 1, 3, 2, _M3, source="D&D Beyond Basic Rules 2024: Barbarian 4 Ability Score Improvement, Orc, Soldier, Savage Attacker, Equipment"),
    5: _r(5, 3, 14, 55, 18, 16, 40, 2, 3, 2, _M3, add=("extra-attack", "fast-movement"), source="D&D Beyond Basic Rules 2024: Barbarian 5 Extra Attack and Fast Movement, Orc, Soldier, Savage Attacker, Equipment"),
    6: _r(6, 3, 14, 65, 18, 16, 40, 2, 4, 2, _M3, add=("mindless-rage",), source="D&D Beyond Basic Rules 2024: Barbarian 6 Path of the Berserker Mindless Rage, Orc, Soldier, Savage Attacker, Equipment"),
    7: _r(7, 3, 14, 75, 18, 16, 40, 2, 4, 2, _M3, add=("feral-instinct", "instinctive-pounce"), source="D&D Beyond Basic Rules 2024: Barbarian 7 Feral Instinct and Instinctive Pounce"),
    8: _r(8, 3, 14, 85, 20, 16, 40, 2, 4, 2, _M3, source="D&D Beyond Basic Rules 2024: Barbarian 8 Ability Score Improvement (+2 Strength)"),
    9: _r(9, 4, 14, 95, 20, 16, 40, 2, 4, 3, _M3, add=("brutal-strike",), ignored=("hamstring-blow",), source="D&D Beyond Basic Rules 2024: Barbarian 9 Brutal Strike"),
    10: _r(10, 4, 14, 105, 20, 16, 40, 2, 4, 3, _M4, add=("retaliation",), source="D&D Beyond Basic Rules 2024: Barbarian 10 Berserker Retaliation"),
    11: _r(11, 4, 14, 115, 20, 16, 40, 2, 4, 3, _M4, add=("relentless-rage",), source="D&D Beyond Basic Rules 2024: Barbarian 11 Relentless Rage"),
    12: _r(12, 4, 15, 137, 20, 18, 40, 2, 5, 3, _M4, source="D&D Beyond Basic Rules 2024: Barbarian 12 Ability Score Improvement (+2 Constitution)"),
    13: _r(13, 5, 15, 148, 20, 18, 40, 2, 5, 3, _M4, add=("improved-brutal-strike",), source="D&D Beyond Basic Rules 2024: Barbarian 13 Improved Brutal Strike"),
    14: _r(14, 5, 15, 159, 20, 18, 40, 2, 5, 3, _M4, add=("intimidating-presence",), source="D&D Beyond Basic Rules 2024: Barbarian 14 Berserker Intimidating Presence"),
    15: _r(15, 5, 15, 170, 20, 18, 40, 2, 5, 3, _M4, add=("persistent-rage",), source="D&D Beyond Basic Rules 2024: Barbarian 15 Persistent Rage"),
    16: _r(16, 5, 16, 197, 20, 20, 40, 2, 5, 4, _M4, source="D&D Beyond Basic Rules 2024: Barbarian 16 Ability Score Improvement (+2 Constitution)"),
    17: _r(17, 6, 16, 209, 20, 20, 40, 2, 6, 4, _M4, add=("brutal-strike-2d10",), remove=("brutal-strike",), source="D&D Beyond Basic Rules 2024: Barbarian 17 Improved Brutal Strike"),
    18: _r(18, 6, 16, 221, 20, 20, 40, 2, 6, 4, _M4, add=("indomitable-might",), source="D&D Beyond Basic Rules 2024: Barbarian 18 Indomitable Might"),
    19: _r(19, 6, 16, 233, 21, 20, 40, 2, 6, 4, _M4, add=("boon-irresistible-offense",), source="D&D Beyond Basic Rules 2024: Barbarian 19 Boon of Irresistible Offense (+1 Strength)"),
    20: _r(20, 6, 18, 285, 25, 24, 40, 2, 6, 4, _M4, add=("primal-champion",), source="D&D Beyond Basic Rules 2024: Barbarian 20 Primal Champion"),
}


def barbarian_combat_features(level: int) -> tuple[str, ...]:
    if level not in BARBARIAN_COMBAT_LEVELS:
        raise ValueError(f"Barbarian level {level} must be between 1 and 20.")
    active: list[str] = []
    for current in range(1, level + 1):
        row = BARBARIAN_COMBAT_LEVELS[current]
        active = [feature for feature in active if feature not in row.features_removed]
        active.extend(feature for feature in row.features_added if feature not in active)
    return tuple(active)


def barbarian_arena_ignored(level: int) -> tuple[str, ...]:
    ignored: list[str] = []
    for current in range(1, level + 1):
        ignored.extend(item for item in BARBARIAN_COMBAT_LEVELS[current].arena_ignored if item not in ignored)
    return tuple(ignored)
