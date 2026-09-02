from __future__ import annotations

from dataclasses import dataclass

from app.content.combat_build_variants import combat_build_variants_for
from app.content.hero_progressions import HERO_BY_CLASS


@dataclass(frozen=True)
class HeroVariantFamily:
    class_id: str
    hero_name: str
    subclass_id: str
    subclass_name: str
    variant_ids: tuple[str, ...]
    branch_level: int = 3

    @property
    def expected_variant_count(self) -> int:
        return 4 if self.class_id == "fighter" else 3


def hero_variant_family(class_id: str) -> HeroVariantFamily:
    hero = HERO_BY_CLASS[class_id]
    variants = combat_build_variants_for(class_id)
    family = HeroVariantFamily(
        class_id=class_id,
        hero_name=hero.hero_name,
        subclass_id=hero.subclass_id,
        subclass_name=hero.subclass_name,
        variant_ids=tuple(variant.id for variant in variants),
    )
    if len(family.variant_ids) != family.expected_variant_count:
        raise RuntimeError(
            f"{class_id} requires {family.expected_variant_count} optimized variants; "
            f"found {len(family.variant_ids)}."
        )
    return family


def all_hero_variant_families() -> tuple[HeroVariantFamily, ...]:
    return tuple(hero_variant_family(class_id) for class_id in HERO_BY_CLASS)
