from __future__ import annotations

from app.content.canonical_hero_policy import canonical_template_id
from app.content.certified_heroes import build_certified_hero_registry
from app.content.hero_progressions import CANONICAL_BUILD_ID, CANONICAL_BUILD_NAME, CANONICAL_HEROES
from app.domain.catalog import CoverageStatus, HeroCatalogCard

SOURCE = "SRD 5.2.1 / 2024 Free Rules"


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
        return HeroCatalogCard(
            **common, coverage_status=CoverageStatus.RAW_READY, runnable_template_id=template_id,
        )
    return HeroCatalogCard(
        **common,
        coverage_status=CoverageStatus.BLOCKED,
        blockers=["hero-level-not-certified", "combat-feature-coverage-not-certified"],
    )


def build_hero_catalog() -> list[HeroCatalogCard]:
    ready_builds = build_certified_hero_registry()
    return [
        _hero_card(hero, level, ready_builds)
        for hero in CANONICAL_HEROES
        for level in range(1, 21)
    ]
