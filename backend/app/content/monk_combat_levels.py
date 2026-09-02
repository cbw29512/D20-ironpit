from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MonkCombatLevel:
    level: int
    proficiency_bonus: int
    martial_arts_die: int
    focus_points: int
    unarmored_movement_bonus_ft: int
    features_added: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()


_ROWS = {
    1: (2, 6, 0, 0, ("martial-arts", "unarmored-defense"), ()),
    2: (2, 6, 2, 10, ("monks-focus", "unarmored-movement", "uncanny-metabolism"), ()),
    3: (2, 6, 3, 10, ("deflect-attacks",), ()),
    4: (2, 6, 4, 10, (), ("slow-fall",)),
    5: (3, 8, 5, 10, ("extra-attack", "stunning-strike"), ()),
    6: (3, 8, 6, 15, ("empowered-strikes",), ()),
    7: (3, 8, 7, 15, ("evasion",), ()),
    8: (3, 8, 8, 15, (), ()),
    9: (4, 8, 9, 15, (), ("acrobatic-movement",)),
    10: (4, 8, 10, 20, ("heightened-focus", "self-restoration"), ()),
    11: (4, 10, 11, 20, (), ()),
    12: (4, 10, 12, 20, (), ()),
    13: (5, 10, 13, 20, ("deflect-energy",), ()),
    14: (5, 10, 14, 25, ("disciplined-survivor",), ()),
    15: (5, 10, 15, 25, ("perfect-focus",), ()),
    16: (5, 10, 16, 25, (), ()),
    17: (6, 12, 17, 25, (), ()),
    18: (6, 12, 18, 30, ("superior-defense",), ()),
    19: (6, 12, 19, 30, ("boon-irresistible-offense",), ()),
    20: (6, 12, 20, 30, ("body-and-mind",), ()),
}

MONK_COMBAT_LEVELS = {
    level: MonkCombatLevel(level, pb, die, focus, movement, add, ignored)
    for level, (pb, die, focus, movement, add, ignored) in _ROWS.items()
}


def monk_combat_features(level: int) -> tuple[str, ...]:
    if level not in MONK_COMBAT_LEVELS:
        raise ValueError(f"Monk level {level} must be between 1 and 20.")
    active: list[str] = []
    for current in range(1, level + 1):
        for feature in MONK_COMBAT_LEVELS[current].features_added:
            if feature not in active:
                active.append(feature)
    return tuple(active)
