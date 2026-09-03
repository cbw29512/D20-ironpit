from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

from app.content.canonical_class_combat_spines import CANONICAL_CLASS_COMBAT_SPINES
from app.content.combat_build_choice_overlays import COMBAT_BUILD_CHOICE_OVERLAYS
from app.content.combat_build_variants import get_combat_build_variant
from app.content.hero_combat_feature_registry import SUPPORTED_HERO_ENGINE_FEATURES
from app.content.hero_variant_policy import TARGET_SUBCLASSES
from app.content.subclass_combat_overlays import SUBCLASS_COMBAT_OVERLAYS, subclass_feature_ids_for_class
from app.content.subclass_specializations import specializations_for_class


@dataclass(frozen=True)
class RosterMechanicRequirement:
    id: str
    kinds: tuple[str, ...]
    owners: tuple[str, ...]
    status: str

    @property
    def demand_count(self) -> int:
        return len(self.owners)


def derive_roster_mechanic_requirements(
    capability_statuses: Mapping[str, str],
) -> tuple[RosterMechanicRequirement, ...]:
    """Derive one deduplicated mechanic backlog from the finished 12-class roster."""
    items: dict[str, dict[str, set[str]]] = {}

    def add(mechanic_id: str, kind: str, owner: str, *, ignored: bool = False) -> None:
        item = items.setdefault(mechanic_id, {"kinds": set(), "owners": set(), "active": set()})
        item["kinds"].add(kind)
        item["owners"].add(owner)
        if not ignored:
            item["active"].add(owner)

    for class_id, rows in CANONICAL_CLASS_COMBAT_SPINES.items():
        owner = f"{class_id}/base"
        subclass_ids = subclass_feature_ids_for_class(class_id)
        for row in rows.values():
            for feature_id in (*getattr(row, "features_added", ()), *getattr(row, "features_removed", ())):
                if feature_id not in subclass_ids:
                    add(feature_id, "base-feature", owner)
            for feature_id in getattr(row, "arena_ignored", ()):
                add(feature_id, "arena-ignored", owner, ignored=True)

    for subclass_id, overlay in SUBCLASS_COMBAT_OVERLAYS.items():
        owner = f"{overlay.class_id}/{subclass_id}"
        for delta in overlay.deltas.values():
            for feature_id in (*delta.features_added, *delta.features_removed):
                add(feature_id, "subclass-feature", owner)
            for feature_id in delta.arena_ignored:
                add(feature_id, "arena-ignored", owner, ignored=True)

    for class_id in TARGET_SUBCLASSES:
        for spec in specializations_for_class(class_id):
            owner = f"{class_id}/{spec.subclass_id}"
            if spec.spell_package_id:
                add(f"spell-package:{spec.spell_package_id}", "spell-package", owner)
            for choice_id in spec.feature_choice_ids:
                add(f"feature-choice:{choice_id}", "feature-choice", owner)

    for (class_id, build_id), overlay in COMBAT_BUILD_CHOICE_OVERLAYS.items():
        subclass_id = get_combat_build_variant(class_id, build_id).required_subclass_id
        owner = f"{class_id}/{subclass_id}"
        for capability_id in overlay.required_capabilities:
            add(capability_id, "loadout-capability", owner)
        for capability_id in overlay.arena_ignored:
            add(capability_id, "arena-ignored", owner, ignored=True)

    requirements: list[RosterMechanicRequirement] = []
    for mechanic_id, item in items.items():
        if mechanic_id in capability_statuses:
            status = capability_statuses[mechanic_id]
        elif mechanic_id in SUPPORTED_HERO_ENGINE_FEATURES:
            status = "supported"
        elif not item["active"]:
            status = "arena_out_of_scope"
        else:
            status = "planned"
        requirements.append(RosterMechanicRequirement(
            id=mechanic_id,
            kinds=tuple(sorted(item["kinds"])),
            owners=tuple(sorted(item["owners"])),
            status=status,
        ))
    return tuple(sorted(requirements, key=lambda item: item.id))
