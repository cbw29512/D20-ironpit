from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RogueCombatLevel:
    level: int
    proficiency_bonus: int
    sneak_attack_d6: int
    features_added: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()


_ROWS = {
    1: (2, 1, ("sneak-attack", "weapon-mastery"), ("expertise", "thieves-cant")),
    2: (2, 1, (), ("cunning-action",)),
    3: (2, 2, ("steady-aim",), ()),
    4: (2, 2, (), ()),
    5: (3, 3, ("cunning-strike", "uncanny-dodge"), ()),
    6: (3, 3, (), ("expertise",)),
    7: (3, 4, ("evasion",), ("reliable-talent",)),
    8: (3, 4, (), ()),
    9: (4, 5, (), ()),
    10: (4, 5, (), ()),
    11: (4, 6, ("improved-cunning-strike",), ()),
    12: (4, 6, (), ()),
    13: (5, 7, (), ()),
    14: (5, 7, ("devious-strikes",), ()),
    15: (5, 8, ("slippery-mind",), ()),
    16: (5, 8, (), ()),
    17: (6, 9, (), ()),
    18: (6, 9, ("elusive",), ()),
    19: (6, 10, ("rogue-epic-boon",), ()),
    20: (6, 10, ("stroke-of-luck",), ()),
}

ROGUE_COMBAT_LEVELS = {
    level: RogueCombatLevel(level, pb, sneak, add, ignored)
    for level, (pb, sneak, add, ignored) in _ROWS.items()
}
