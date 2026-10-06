from __future__ import annotations

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.character_builds import AbilityScores
from app.domain.movement import MovementModes

_ABILITY_KEYS = {
    "str": "strength", "dex": "dexterity", "con": "constitution",
    "int": "intelligence", "wis": "wisdom", "cha": "charisma",
}
FULL_ABILITIES_2014 = tuple(_ABILITY_KEYS.values())


def ability_values_2014(monster: SourceMonster2014) -> dict[str, int]:
    normalized = {
        _ABILITY_KEYS.get(key.lower(), key.lower()): value
        for key, value in monster.abilities.items()
    }
    missing = set(FULL_ABILITIES_2014) - set(normalized)
    if missing:
        raise ValueError(f"{monster.id} is missing ability scores: {sorted(missing)}")
    return {name: int(normalized[name]) for name in FULL_ABILITIES_2014}


def save_bonuses_2014(
    monster: SourceMonster2014,
    scores: AbilityScores,
) -> dict[str, int]:
    bonuses = {name: scores.modifier(name) for name in FULL_ABILITIES_2014}
    for key, value in monster.saving_throws.items():
        name = _ABILITY_KEYS.get(key.lower(), key.lower())
        if name not in bonuses:
            raise ValueError(f"{monster.id} has unknown saving throw ability {key!r}")
        bonuses[name] = int(value)
    return bonuses


def movement_modes_2014(monster: SourceMonster2014) -> MovementModes:
    speed = {
        key.lower().replace("_ft", ""): int(value)
        for key, value in monster.speed.items()
    }
    return MovementModes(
        walk_ft=speed.get("walk", speed.get("speed", 0)),
        fly_ft=speed.get("fly", 0),
        climb_ft=speed.get("climb", 0),
        swim_ft=speed.get("swim", 0),
        burrow_ft=speed.get("burrow", 0),
    )


def attack_id_2014(monster: SourceMonster2014, source_attack_id: str) -> str:
    return f"2014-{monster.id}-{source_attack_id}".replace("--", "-")
