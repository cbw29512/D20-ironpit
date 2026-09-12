from __future__ import annotations

from dataclasses import dataclass

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.hero_progressions import CANONICAL_HEROES


@dataclass(frozen=True)
class PregenCertificationCandidate:
    class_id: str
    certified_through: int
    next_level: int
    unsupported_features: tuple[str, ...]

    @property
    def blocker_count(self) -> int:
        return len(self.unsupported_features)

    @property
    def ready(self) -> bool:
        return self.blocker_count == 0


def certified_level_by_class() -> dict[str, int]:
    """Return the highest sequentially registered certification level per class."""
    certified = {hero.class_id: 0 for hero in CANONICAL_HEROES}
    for progression in CERTIFIED_HERO_PROGRESSIONS:
        certified[progression.class_id] = len(progression.profile_builders)
    return certified


def build_pregen_certification_frontier() -> tuple[PregenCertificationCandidate, ...]:
    """Rank each class's next sequential snapshot by unsupported engine work.

    Certification is intentionally sequential, so later levels are not useful work until the
    current frontier level is certified. Ready/data-only candidates sort first, followed by
    the smallest blocker set and then stable class/level ordering.
    """
    certified = certified_level_by_class()
    candidates: list[PregenCertificationCandidate] = []

    for hero in CANONICAL_HEROES:
        current = certified[hero.class_id]
        if current >= 20:
            continue
        next_level = current + 1
        features = canonical_combat_features(hero.class_id, next_level, hero.subclass_id)
        blockers = unsupported_hero_engine_features(features)
        candidates.append(PregenCertificationCandidate(
            class_id=hero.class_id,
            certified_through=current,
            next_level=next_level,
            unsupported_features=blockers,
        ))

    return tuple(sorted(
        candidates,
        key=lambda item: (item.blocker_count, item.class_id, item.next_level),
    ))
