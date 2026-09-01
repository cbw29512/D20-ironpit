from __future__ import annotations

FULL_CASTER_CLASSES = frozenset({"bard", "cleric", "druid", "sorcerer", "wizard"})

# 2024 full-caster spell slots by character level; tuple index 0 is spell level 1.
_FULL_CASTER_SLOTS: tuple[tuple[int, ...], ...] = (
    (2,),
    (3,),
    (4, 2),
    (4, 3),
    (4, 3, 2),
    (4, 3, 3),
    (4, 3, 3, 1),
    (4, 3, 3, 2),
    (4, 3, 3, 3, 1),
    (4, 3, 3, 3, 2),
    (4, 3, 3, 3, 2, 1),
    (4, 3, 3, 3, 2, 1),
    (4, 3, 3, 3, 2, 1, 1),
    (4, 3, 3, 3, 2, 1, 1),
    (4, 3, 3, 3, 2, 1, 1, 1),
    (4, 3, 3, 3, 2, 1, 1, 1),
    (4, 3, 3, 3, 2, 1, 1, 1, 1),
    (4, 3, 3, 3, 3, 1, 1, 1, 1),
    (4, 3, 3, 3, 3, 2, 1, 1, 1),
    (4, 3, 3, 3, 3, 2, 2, 1, 1),
)


def spell_slot_counts(class_id: str, level: int) -> dict[int, int]:
    if class_id not in FULL_CASTER_CLASSES:
        raise ValueError(f"Spell-slot progression is not yet audited for {class_id}.")
    if not 1 <= level <= 20:
        raise ValueError("Character level must be between 1 and 20.")
    return {
        spell_level: uses
        for spell_level, uses in enumerate(_FULL_CASTER_SLOTS[level - 1], start=1)
        if uses > 0
    }


def spell_slot_resources(class_id: str, level: int) -> dict[str, int]:
    return {f"spell-slot-{spell_level}": uses for spell_level, uses in spell_slot_counts(class_id, level).items()}
