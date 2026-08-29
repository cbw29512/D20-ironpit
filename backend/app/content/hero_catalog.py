from __future__ import annotations

from app.domain.catalog import CoverageStatus, HeroCatalogCard

SOURCE = "SRD 5.2.1 / 2024 Free Rules"

_CLASS_ROWS = [
    ("barbarian", "Barbarian", "path-berserker", "Path of the Berserker"),
    ("bard", "Bard", "college-lore", "College of Lore"),
    ("cleric", "Cleric", "life-domain", "Life Domain"),
    ("druid", "Druid", "circle-land", "Circle of the Land"),
    ("fighter", "Fighter", "champion", "Champion"),
    ("monk", "Monk", "warrior-open-hand", "Warrior of the Open Hand"),
    ("paladin", "Paladin", "oath-devotion", "Oath of Devotion"),
    ("ranger", "Ranger", "hunter", "Hunter"),
    ("rogue", "Rogue", "thief", "Thief"),
    ("sorcerer", "Sorcerer", "draconic-sorcery", "Draconic Sorcery"),
    ("warlock", "Warlock", "fiend-patron", "Fiend Patron"),
    ("wizard", "Wizard", "evoker", "Evoker"),
]

_READY_SLOTS = {
    ("fighter", 1): ("Aldric Vane", "aldric-vane-l1"),
    ("rogue", 1): ("Mara Quickstep", "mara-quickstep-l1"),
}


def _hero_card(class_row: tuple[str, str, str, str], level: int) -> HeroCatalogCard:
    class_id, class_name, subclass_id, subclass_name = class_row
    ready = _READY_SLOTS.get((class_id, level))
    unlocked_subclass_id = subclass_id if level >= 3 else None
    unlocked_subclass_name = subclass_name if level >= 3 else None
    if ready:
        name, template_id = ready
        return HeroCatalogCard(
            id=f"hero-2024-{class_id}-l{level}",
            name=name,
            class_id=class_id,
            class_name=class_name,
            level=level,
            subclass_id=unlocked_subclass_id,
            subclass_name=unlocked_subclass_name,
            source=SOURCE,
            coverage_status=CoverageStatus.RAW_READY,
            runnable_template_id=template_id,
        )
    return HeroCatalogCard(
        id=f"hero-2024-{class_id}-l{level}",
        name=f"{class_name} {level}",
        class_id=class_id,
        class_name=class_name,
        level=level,
        subclass_id=unlocked_subclass_id,
        subclass_name=unlocked_subclass_name,
        source=SOURCE,
        coverage_status=CoverageStatus.BLOCKED,
        blockers=["pregen-build-not-certified", "class-level-mechanics-not-certified"],
    )


def build_hero_catalog() -> list[HeroCatalogCard]:
    return [
        _hero_card(class_row, level)
        for class_row in _CLASS_ROWS
        for level in range(1, 21)
    ]
