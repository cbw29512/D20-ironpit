from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Fighter2014Level:
    level: int
    proficiency_bonus: int
    max_hp: int
    strength: int
    dexterity: int
    constitution: int
    attack_count: int
    second_wind_uses: int
    action_surge_uses: int
    indomitable_uses: int
    critical_hit_minimum: int
    remarkable_athlete_bonus: int
    fighting_styles: tuple[str, ...]
    source: str


_SOURCE = "D&D Beyond Basic Rules 2014: Half-Orc Fighter (Champion), Soldier, Equipment"


def _r(
    level: int,
    pb: int,
    hp: int,
    strength: int,
    constitution: int,
    attacks: int,
    action_surge: int,
    indomitable: int,
    critical_minimum: int,
    remarkable_athlete_bonus: int = 0,
    styles: tuple[str, ...] = ("Defense",),
) -> Fighter2014Level:
    return Fighter2014Level(
        level=level,
        proficiency_bonus=pb,
        max_hp=hp,
        strength=strength,
        dexterity=13,
        constitution=constitution,
        attack_count=attacks,
        second_wind_uses=1,
        action_surge_uses=action_surge,
        indomitable_uses=indomitable,
        critical_hit_minimum=critical_minimum,
        remarkable_athlete_bonus=remarkable_athlete_bonus,
        fighting_styles=styles,
        source=_SOURCE,
    )


FIGHTER_2014_LEVELS: dict[int, Fighter2014Level] = {
    1: _r(1, 2, 12, 17, 15, 1, 0, 0, 20),
    2: _r(2, 2, 20, 17, 15, 1, 1, 0, 20),
    3: _r(3, 2, 28, 17, 15, 1, 1, 0, 19),
    4: _r(4, 2, 40, 18, 16, 1, 1, 0, 19),
    5: _r(5, 3, 49, 18, 16, 2, 1, 0, 19),
    6: _r(6, 3, 58, 20, 16, 2, 1, 0, 19),
    7: _r(7, 3, 67, 20, 16, 2, 1, 0, 19, 2),
    8: _r(8, 3, 84, 20, 18, 2, 1, 0, 19, 2),
    9: _r(9, 4, 94, 20, 18, 2, 1, 1, 19, 2),
    10: _r(10, 4, 104, 20, 18, 2, 1, 1, 19, 2, ("Defense", "Archery")),
}
