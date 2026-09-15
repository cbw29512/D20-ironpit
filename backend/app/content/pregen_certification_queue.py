from __future__ import annotations

from dataclasses import dataclass

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.canonical_spell_packages import CANONICAL_SPELLS, build_class_spell_package
from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.hero_progressions import CANONICAL_HEROES


@dataclass(frozen=True)
class PregenCertificationCandidate:
    class_id: str
    certified_through: int
    next_level: int
    unsupported_features: tuple[str, ...]
    content_blockers: tuple[str, ...] = ()

    @property
    def blocker_count(self) -> int:
        return len(self.unsupported_features) + len(self.content_blockers)

    @property
    def blockers(self) -> tuple[str, ...]:
        return self.unsupported_features + self.content_blockers

    @property
    def ready(self) -> bool:
        return self.blocker_count == 0


def certified_level_by_class() -> dict[str, int]:
    """Return the highest sequentially registered certification level per class."""
    certified = {hero.class_id: 0 for hero in CANONICAL_HEROES}
    for progression in CERTIFIED_HERO_PROGRESSIONS:
        certified[progression.class_id] = len(progression.profile_builders)
    return certified


def _spell_package_blockers(class_id: str, level: int) -> tuple[str, ...]:
    if class_id not in CANONICAL_SPELLS:
        return ()
    try:
        build_class_spell_package(class_id, level)  # type: ignore[arg-type]
    except ValueError:
        return ("canonical-spell-package-incomplete",)
    return ()


def build_pregen_certification_frontier() -> tuple[PregenCertificationCandidate, ...]:
    """Rank each class's next sequential snapshot by all known fail-closed work."""
    certified = certified_level_by_class()
    candidates: list[PregenCertificationCandidate] = []

    for hero in CANONICAL_HEROES:
        current = certified[hero.class_id]
        if current >= 20:
            continue
        next_level = current + 1
        features = canonical_combat_features(hero.class_id, next_level, hero.subclass_id)
        candidates.append(PregenCertificationCandidate(
            class_id=hero.class_id,
            certified_through=current,
            next_level=next_level,
            unsupported_features=unsupported_hero_engine_features(features),
            content_blockers=_spell_package_blockers(hero.class_id, next_level),
        ))

    return tuple(sorted(
        candidates,
        key=lambda item: (item.blocker_count, item.class_id, item.next_level),
    ))
