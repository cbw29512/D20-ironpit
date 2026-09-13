from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.hero_progressions import CANONICAL_HEROES
from app.content.pregen_certification_queue import certified_level_by_class


@dataclass(frozen=True)
class PregenBlockerYield:
    feature_id: str
    frontier_classes: tuple[str, ...]
    remaining_snapshots: int

    @property
    def frontier_count(self) -> int:
        return len(self.frontier_classes)


@dataclass(frozen=True)
class PregenBlockerBundleYield:
    feature_ids: tuple[str, ...]
    frontier_classes: tuple[str, ...]
    remaining_snapshots: int

    @property
    def frontier_count(self) -> int:
        return len(self.frontier_classes)


def _remaining_blockers() -> list[tuple[str, int, tuple[str, ...]]]:
    certified = certified_level_by_class()
    rows: list[tuple[str, int, tuple[str, ...]]] = []
    for hero in CANONICAL_HEROES:
        for level in range(certified[hero.class_id] + 1, 21):
            features = canonical_combat_features(hero.class_id, level, hero.subclass_id)
            blockers = unsupported_hero_engine_features(features)
            rows.append((hero.class_id, level, blockers))
    return rows


def build_pregen_blocker_yields() -> tuple[PregenBlockerYield, ...]:
    certified = certified_level_by_class()
    snapshots: dict[str, int] = defaultdict(int)
    frontier: dict[str, set[str]] = defaultdict(set)
    for class_id, level, blockers in _remaining_blockers():
        for feature_id in blockers:
            snapshots[feature_id] += 1
            if level == certified[class_id] + 1:
                frontier[feature_id].add(class_id)
    return tuple(sorted(
        (
            PregenBlockerYield(feature_id, tuple(sorted(frontier[feature_id])), count)
            for feature_id, count in snapshots.items()
        ),
        key=lambda item: (-item.frontier_count, -item.remaining_snapshots, item.feature_id),
    ))


def build_pregen_blocker_bundle_yields() -> tuple[PregenBlockerBundleYield, ...]:
    certified = certified_level_by_class()
    snapshots: dict[tuple[str, ...], int] = defaultdict(int)
    frontier: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for class_id, level, blockers in _remaining_blockers():
        if not blockers:
            continue
        bundle = tuple(sorted(blockers))
        snapshots[bundle] += 1
        if level == certified[class_id] + 1:
            frontier[bundle].add(class_id)
    return tuple(sorted(
        (
            PregenBlockerBundleYield(bundle, tuple(sorted(frontier[bundle])), count)
            for bundle, count in snapshots.items()
        ),
        key=lambda item: (-item.frontier_count, -item.remaining_snapshots, item.feature_ids),
    ))
