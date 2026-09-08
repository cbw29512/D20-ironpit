from __future__ import annotations

from app.content.canonical_class_combat_spines import canonical_arena_ignored, canonical_combat_features
from app.content.canonical_hero_policy import CASTER_CLASS_IDS, canonical_spell_package, canonical_template_id
from app.content.certified_heroes import build_certified_hero_registry
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.hero_progressions import CANONICAL_BUILD_ID, CANONICAL_BUILD_NAME, CANONICAL_HEROES
from app.domain.catalog import CoverageStatus, HeroCatalogCard

SOURCE = "SRD 5.2.1 / 2024 Free Rules"


def _blocked_reasons(class_id: str, level: int) -> list[str]:
    ignored = set(canonical_arena_ignored(class_id, level))
    features = tuple(feature for feature in canonical_combat_features(class_id, level) if feature not in ignored)
    unsupported = unsupported_hero_engine_features(features)
    blockers = ["hero-level-not-certified"]
    blockers.extend(f"unsupported-combat-feature:{feature}" for feature in unsupported)
    if class_id in CASTER_CLASS_IDS:
        try:
            canonical_spell_package(class_id, level)
        except ValueError:
            blockers.append("canonical-spell-package-incomplete")
    if len(blockers) == 1:
        blockers.append("runtime-template-not-compiled")
    return blockers


def _hero_card(hero, level: int, ready_builds: dict[tuple[str, int, str], tuple[str, str]]) -> HeroCatalogCard:
    ready = ready_builds.get((hero.class_id, level, CANONICAL_BUILD_ID))
    common = dict(
        id=f"hero-2024-{hero.class_id}-l{level}",
        name=hero.hero_name,
        class_id=hero.class_id,
        class_name=hero.class_name,
        level=level,
        build_id=CANONICAL_BUILD_ID,
        build_name=CANONICAL_BUILD_NAME,
        subclass_id=hero.subclass_id if level >= 3 else None,
        subclass_name=hero.subclass_name if level >= 3 else None,
        source=SOURCE,
    )
    if ready:
        name, template_id = ready
        if name != hero.hero_name:
            raise ValueError(f"Certified {hero.class_id} hero name drifted: {name} != {hero.hero_name}.")
        expected_template_id = canonical_template_id(hero.class_id, level)
        if template_id != expected_template_id:
            raise ValueError(
                f"Certified {hero.class_id} level {level} runtime identity drifted: "
                f"{template_id} != {expected_template_id}."
            )
        if hero.class_id in CASTER_CLASS_IDS:
            canonical_spell_package(hero.class_id, level)
        return HeroCatalogCard(
            **common, coverage_status=CoverageStatus.RAW_READY, runnable_template_id=template_id,
        )
    return HeroCatalogCard(
        **common,
        coverage_status=CoverageStatus.BLOCKED,
        blockers=_blocked_reasons(hero.class_id, level),
    )


def build_hero_catalog() -> list[HeroCatalogCard]:
    ready_builds = build_certified_hero_registry()
    return [
        _hero_card(hero, level, ready_builds)
        for hero in CANONICAL_HEROES
        for level in range(1, 21)
    ]
