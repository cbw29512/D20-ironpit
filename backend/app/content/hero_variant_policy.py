from __future__ import annotations

from dataclasses import dataclass

from app.content.hero_progressions import HERO_BY_CLASS
from app.content.subclass_specializations import specializations_for_class


@dataclass(frozen=True)
class HeroSubclassFamily:
    class_id: str
    hero_name: str
    subclass_ids: tuple[str, ...]
    target_subclass_count: int
    branch_level: int = 3

    @property
    def migration_complete(self) -> bool:
        return len(self.subclass_ids) == self.target_subclass_count


def hero_subclass_family(class_id: str) -> HeroSubclassFamily:
    hero = HERO_BY_CLASS[class_id]
    specializations = specializations_for_class(class_id)
    subclass_ids = tuple(item.subclass_id for item in specializations) or (hero.subclass_id,)
    return HeroSubclassFamily(
        class_id=class_id,
        hero_name=hero.hero_name,
        subclass_ids=subclass_ids,
        target_subclass_count=4 if class_id == "fighter" else 3,
    )


def all_hero_subclass_families() -> tuple[HeroSubclassFamily, ...]:
    return tuple(hero_subclass_family(class_id) for class_id in HERO_BY_CLASS)
