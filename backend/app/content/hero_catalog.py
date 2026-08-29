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

_BUILD_ROWS = {
    "barbarian": [("great-weapon", "Great Weapon"), ("axe-shield", "Axe & Shield"), ("dual-wielder", "Dual Wielder")],
    "bard": [("support", "Support"), ("duelist", "Duelist"), ("controller", "Controller")],
    "cleric": [("guardian", "Guardian"), ("healer", "Healer"), ("war-priest", "War Priest")],
    "druid": [("wild-shaper", "Wild Shaper"), ("primal-caster", "Primal Caster"), ("warden", "Warden")],
    "fighter": [("guardian", "Sword & Shield"), ("great-weapon", "Great Weapon"), ("archer", "Archer")],
    "monk": [("striker", "Striker"), ("skirmisher", "Skirmisher"), ("defender", "Defender")],
    "paladin": [("guardian", "Guardian"), ("great-weapon", "Great Weapon"), ("avenger", "Avenger")],
    "ranger": [("archer", "Archer"), ("dual-wielder", "Dual Wielder"), ("warden", "Warden")],
    "rogue": [("skirmisher", "Skirmisher"), ("archer", "Archer"), ("duelist", "Duelist")],
    "sorcerer": [("blaster", "Blaster"), ("controller", "Controller"), ("survivor", "Survivor")],
    "warlock": [("eldritch-blaster", "Eldritch Blaster"), ("blade", "Blade"), ("controller", "Controller")],
    "wizard": [("evoker", "Evoker"), ("controller", "Controller"), ("defender", "Defender")],
}

_READY_BUILDS = {
    ("fighter", 1, "guardian"): ("Aldric Vane", "aldric-vane-l1"),
    ("fighter", 1, "great-weapon"): ("Brom Ironmark", "brom-ironmark-l1"),
    ("fighter", 1, "archer"): ("Selene Asharrow", "selene-asharrow-l1"),
    ("rogue", 1, "skirmisher"): ("Mara Quickstep", "mara-quickstep-l1"),
}


def _card_id(class_id: str, level: int, build_id: str, build_index: int) -> str:
    base = f"hero-2024-{class_id}-l{level}"
    return base if build_index == 0 else f"{base}-{build_id}"


def _hero_card(
    class_row: tuple[str, str, str, str],
    level: int,
    build: tuple[str, str],
    build_index: int,
) -> HeroCatalogCard:
    class_id, class_name, subclass_id, subclass_name = class_row
    build_id, build_name = build
    ready = _READY_BUILDS.get((class_id, level, build_id))
    subclass_ready = level >= 3
    common = dict(
        id=_card_id(class_id, level, build_id, build_index),
        class_id=class_id,
        class_name=class_name,
        level=level,
        build_id=build_id,
        build_name=build_name,
        subclass_id=subclass_id if subclass_ready else None,
        subclass_name=subclass_name if subclass_ready else None,
        source=SOURCE,
    )
    if ready:
        name, template_id = ready
        return HeroCatalogCard(
            **common,
            name=name,
            coverage_status=CoverageStatus.RAW_READY,
            runnable_template_id=template_id,
        )
    return HeroCatalogCard(
        **common,
        name=f"{class_name} {level} — {build_name}",
        coverage_status=CoverageStatus.BLOCKED,
        blockers=["pregen-build-not-certified", "class-level-mechanics-not-certified"],
    )


def build_hero_catalog() -> list[HeroCatalogCard]:
    return [
        _hero_card(class_row, level, build, build_index)
        for class_row in _CLASS_ROWS
        for level in range(1, 21)
        for build_index, build in enumerate(_BUILD_ROWS[class_row[0]])
    ]
