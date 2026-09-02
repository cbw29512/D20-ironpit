from __future__ import annotations

from dataclasses import dataclass

from app.content.hero_progressions import HERO_BY_CLASS
from app.content.subclass_specializations import specializations_for_class


TARGET_SUBCLASSES: dict[str, tuple[str, ...]] = {
    "barbarian": ("path-berserker", "path-wild-heart", "path-zealot"),
    "bard": ("college-lore", "college-valor", "college-glamour"),
    "cleric": ("life-domain", "light-domain", "war-domain"),
    "druid": ("circle-land", "circle-moon", "circle-sea"),
    "fighter": ("champion", "battle-master", "eldritch-knight", "psi-warrior"),
    "monk": ("warrior-open-hand", "warrior-shadow", "warrior-elements"),
    "paladin": ("oath-devotion", "oath-vengeance", "oath-ancients"),
    "ranger": ("hunter", "gloom-stalker", "beastmaster"),
    "rogue": ("thief", "assassin", "arcane-trickster"),
    "sorcerer": ("draconic-sorcery", "aberrant-sorcery", "clockwork-sorcery"),
    "warlock": ("fiend-patron", "great-old-one-patron", "celestial-patron"),
    "wizard": ("evoker", "illusionist", "abjurer"),
}


@dataclass(frozen=True)
class HeroSubclassFamily:
    class_id: str
    hero_name: str
    target_subclass_ids: tuple[str, ...]
    audited_subclass_ids: tuple[str, ...]
    branch_level: int = 3

    @property
    def migration_complete(self) -> bool:
        return self.audited_subclass_ids == self.target_subclass_ids


def hero_subclass_family(class_id: str) -> HeroSubclassFamily:
    hero = HERO_BY_CLASS[class_id]
    specializations = specializations_for_class(class_id)
    audited = tuple(item.subclass_id for item in specializations) or (hero.subclass_id,)
    return HeroSubclassFamily(
        class_id=class_id,
        hero_name=hero.hero_name,
        target_subclass_ids=TARGET_SUBCLASSES[class_id],
        audited_subclass_ids=audited,
    )


def all_hero_subclass_families() -> tuple[HeroSubclassFamily, ...]:
    return tuple(hero_subclass_family(class_id) for class_id in HERO_BY_CLASS)
