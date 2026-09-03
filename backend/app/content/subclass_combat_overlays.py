from __future__ import annotations

from dataclasses import dataclass

from app.content.barbarian_subclass_overlay_data import BARBARIAN_SUBCLASS_DELTA_DATA
from app.content.bard_subclass_overlay_data import BARD_SUBCLASS_DELTA_DATA
from app.content.cleric_subclass_overlay_data import CLERIC_SUBCLASS_DELTA_DATA
from app.content.druid_subclass_overlay_data import DRUID_SUBCLASS_DELTA_DATA
from app.content.fighter_subclass_overlay_data import FIGHTER_SUBCLASS_DELTA_DATA
from app.content.monk_subclass_overlay_data import MONK_SUBCLASS_DELTA_DATA
from app.content.paladin_subclass_overlay_data import PALADIN_SUBCLASS_DELTA_DATA
from app.content.ranger_subclass_overlay_data import RANGER_SUBCLASS_DELTA_DATA
from app.content.rogue_subclass_overlay_data import ROGUE_SUBCLASS_DELTA_DATA
from app.content.sorcerer_subclass_overlay_data import SORCERER_SUBCLASS_DELTA_DATA
from app.content.wizard_subclass_overlay_data import WIZARD_SUBCLASS_DELTA_DATA
from app.content.warlock_subclass_overlay_data import WARLOCK_SUBCLASS_DELTA_DATA


@dataclass(frozen=True)
class SubclassCombatDelta:
    level: int
    features_added: tuple[str, ...] = ()
    features_removed: tuple[str, ...] = ()
    arena_ignored: tuple[str, ...] = ()


@dataclass(frozen=True)
class SubclassCombatOverlay:
    class_id: str
    subclass_id: str
    deltas: dict[int, SubclassCombatDelta]


def _overlay(class_id: str, subclass_id: str, rows: dict[int, dict[str, tuple[str, ...]]]) -> SubclassCombatOverlay:
    return SubclassCombatOverlay(class_id, subclass_id, {
        level: SubclassCombatDelta(
            level,
            tuple(data.get("features_added", ())),
            tuple(data.get("features_removed", ())),
            tuple(data.get("arena_ignored", ())),
        )
        for level, data in rows.items()
    })


SUBCLASS_COMBAT_OVERLAYS: dict[str, SubclassCombatOverlay] = {}
for _class_id, _source in (
    ("barbarian", BARBARIAN_SUBCLASS_DELTA_DATA),
    ("bard", BARD_SUBCLASS_DELTA_DATA),
    ("cleric", CLERIC_SUBCLASS_DELTA_DATA),
    ("druid", DRUID_SUBCLASS_DELTA_DATA),
    ("fighter", FIGHTER_SUBCLASS_DELTA_DATA),
    ("monk", MONK_SUBCLASS_DELTA_DATA),
    ("paladin", PALADIN_SUBCLASS_DELTA_DATA),
    ("ranger", RANGER_SUBCLASS_DELTA_DATA),
    ("rogue", ROGUE_SUBCLASS_DELTA_DATA),
    ("sorcerer", SORCERER_SUBCLASS_DELTA_DATA),
    ("wizard", WIZARD_SUBCLASS_DELTA_DATA),
    ("warlock", WARLOCK_SUBCLASS_DELTA_DATA),
):
    for _subclass_id, _rows in _source.items():
        if _subclass_id in SUBCLASS_COMBAT_OVERLAYS:
            raise ValueError(f"Duplicate subclass combat overlay: {_subclass_id}.")
        SUBCLASS_COMBAT_OVERLAYS[_subclass_id] = _overlay(_class_id, _subclass_id, _rows)


def subclass_overlay(subclass_id: str) -> SubclassCombatOverlay:
    try:
        return SUBCLASS_COMBAT_OVERLAYS[subclass_id]
    except KeyError as exc:
        raise ValueError(f"Unknown combat subclass overlay: {subclass_id}.") from exc


def subclass_feature_ids_for_class(class_id: str) -> set[str]:
    ids: set[str] = set()
    for overlay in SUBCLASS_COMBAT_OVERLAYS.values():
        if overlay.class_id == class_id:
            for delta in overlay.deltas.values():
                ids.update(delta.features_added)
                ids.update(delta.features_removed)
    return ids


def subclass_ignored_ids_for_class(class_id: str) -> set[str]:
    ids: set[str] = set()
    for overlay in SUBCLASS_COMBAT_OVERLAYS.values():
        if overlay.class_id == class_id:
            for delta in overlay.deltas.values():
                ids.update(delta.arena_ignored)
    return ids


def subclass_combat_features(subclass_id: str, character_level: int) -> tuple[str, ...]:
    overlay = subclass_overlay(subclass_id)
    if not 1 <= character_level <= 20:
        raise ValueError("Character level must be between 1 and 20.")
    active: list[str] = []
    for current in sorted(level for level in overlay.deltas if level <= character_level):
        delta = overlay.deltas[current]
        active = [feature for feature in active if feature not in delta.features_removed]
        active.extend(feature for feature in delta.features_added if feature not in active)
    return tuple(active)
