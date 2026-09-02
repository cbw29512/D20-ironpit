from __future__ import annotations

from dataclasses import dataclass


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


SUBCLASS_COMBAT_OVERLAYS: dict[str, SubclassCombatOverlay] = {
    "path-berserker": SubclassCombatOverlay("barbarian", "path-berserker", {
        3: SubclassCombatDelta(3, ("frenzy",)),
        6: SubclassCombatDelta(6, ("mindless-rage",)),
        10: SubclassCombatDelta(10, ("retaliation",)),
        14: SubclassCombatDelta(14, ("intimidating-presence",)),
    }),
    "college-lore": SubclassCombatOverlay("bard", "college-lore", {
        3: SubclassCombatDelta(3, ("cutting-words",), arena_ignored=("lore-bonus-proficiencies",)),
        6: SubclassCombatDelta(6, ("magical-discoveries",)),
        14: SubclassCombatDelta(14, ("peerless-skill",)),
    }),
    "life-domain": SubclassCombatOverlay("cleric", "life-domain", {
        3: SubclassCombatDelta(3, ("disciple-of-life", "preserve-life")),
        6: SubclassCombatDelta(6, ("blessed-healer",)),
        17: SubclassCombatDelta(17, ("supreme-healing",)),
    }),
    "circle-land": SubclassCombatOverlay("druid", "circle-land", {
        3: SubclassCombatDelta(3, ("lands-aid", "land-arid-spells")),
        6: SubclassCombatDelta(6, ("natural-recovery",)),
        10: SubclassCombatDelta(10, ("natures-ward-fire",)),
        14: SubclassCombatDelta(14, ("natures-sanctuary",)),
    }),
    "champion": SubclassCombatOverlay("fighter", "champion", {
        3: SubclassCombatDelta(3, ("improved-critical", "remarkable-athlete")),
        7: SubclassCombatDelta(7, ("great-weapon-fighting",)),
        10: SubclassCombatDelta(10, ("heroic-warrior",)),
        15: SubclassCombatDelta(15, ("superior-critical",), ("improved-critical",)),
        18: SubclassCombatDelta(18, ("survivor-defy-death", "survivor-heroic-rally")),
    }),
    "warrior-open-hand": SubclassCombatOverlay("monk", "warrior-open-hand", {
        3: SubclassCombatDelta(3, ("open-hand-technique",)),
        6: SubclassCombatDelta(6, ("wholeness-of-body",)),
        11: SubclassCombatDelta(11, ("fleet-step",)),
        17: SubclassCombatDelta(17, ("quivering-palm",)),
    }),
    "oath-devotion": SubclassCombatOverlay("paladin", "oath-devotion", {
        3: SubclassCombatDelta(3, ("sacred-weapon", "devotion-combat-spells-1")),
        5: SubclassCombatDelta(5, ("devotion-combat-spells-2",)),
        7: SubclassCombatDelta(7, ("aura-of-devotion",)),
        9: SubclassCombatDelta(9, ("devotion-combat-spells-3",)),
        13: SubclassCombatDelta(13, ("devotion-combat-spells-4",)),
        15: SubclassCombatDelta(15, ("smite-of-protection",)),
        17: SubclassCombatDelta(17, ("devotion-combat-spells-5",)),
        20: SubclassCombatDelta(20, ("holy-nimbus",)),
    }),
    "hunter": SubclassCombatOverlay("ranger", "hunter", {
        3: SubclassCombatDelta(3, ("hunters-lore", "hunter-prey-colossus-slayer")),
        7: SubclassCombatDelta(7, ("hunter-multiattack-defense",)),
        11: SubclassCombatDelta(11, ("superior-hunters-prey",)),
        15: SubclassCombatDelta(15, ("superior-hunters-defense",)),
    }),
    "thief": SubclassCombatOverlay("rogue", "thief", {
        3: SubclassCombatDelta(3, ("thief-fast-hands",), arena_ignored=("thief-second-story-work",)),
        9: SubclassCombatDelta(9, ("thief-supreme-sneak",)),
        13: SubclassCombatDelta(13, ("thief-use-magic-device",)),
        17: SubclassCombatDelta(17, ("thiefs-reflexes",)),
    }),
    "draconic-sorcery": SubclassCombatOverlay("sorcerer", "draconic-sorcery", {
        3: SubclassCombatDelta(3, ("draconic-resilience",)),
        6: SubclassCombatDelta(6, ("elemental-affinity-fire",)),
        14: SubclassCombatDelta(14, ("dragon-wings",)),
        18: SubclassCombatDelta(18, ("dragon-companion",)),
    }),
    "fiend-patron": SubclassCombatOverlay("warlock", "fiend-patron", {
        3: SubclassCombatDelta(3, ("dark-ones-blessing", "fiend-combat-spells-2")),
        5: SubclassCombatDelta(5, ("fiend-combat-spells-3",)),
        6: SubclassCombatDelta(6, ("dark-ones-own-luck",)),
        7: SubclassCombatDelta(7, ("fiend-combat-spells-4",)),
        9: SubclassCombatDelta(9, ("fiend-combat-spells-5",)),
        10: SubclassCombatDelta(10, ("fiendish-resilience",)),
        14: SubclassCombatDelta(14, ("hurl-through-hell",)),
    }),
    "evoker": SubclassCombatOverlay("wizard", "evoker", {
        3: SubclassCombatDelta(3, ("potent-cantrip", "evocation-savant")),
        6: SubclassCombatDelta(6, ("sculpt-spells",)),
        10: SubclassCombatDelta(10, ("empowered-evocation",)),
        14: SubclassCombatDelta(14, ("overchannel",)),
    }),
}


def subclass_overlay(subclass_id: str) -> SubclassCombatOverlay:
    try:
        return SUBCLASS_COMBAT_OVERLAYS[subclass_id]
    except KeyError as exc:
        raise ValueError(f"Unknown combat subclass overlay: {subclass_id}.") from exc


def subclass_feature_ids_for_class(class_id: str) -> set[str]:
    ids: set[str] = set()
    for overlay in SUBCLASS_COMBAT_OVERLAYS.values():
        if overlay.class_id != class_id:
            continue
        for delta in overlay.deltas.values():
            ids.update(delta.features_added)
            ids.update(delta.features_removed)
    return ids


def subclass_ignored_ids_for_class(class_id: str) -> set[str]:
    ids: set[str] = set()
    for overlay in SUBCLASS_COMBAT_OVERLAYS.values():
        if overlay.class_id != class_id:
            continue
        for delta in overlay.deltas.values():
            ids.update(delta.arena_ignored)
    return ids


def subclass_combat_features(subclass_id: str, character_level: int) -> tuple[str, ...]:
    overlay = subclass_overlay(subclass_id)
    if not 1 <= character_level <= 20:
        raise ValueError("Character level must be between 1 and 20.")
    active: list[str] = []
    for current in sorted(delta_level for delta_level in overlay.deltas if delta_level <= character_level):
        delta = overlay.deltas[current]
        active = [feature for feature in active if feature not in delta.features_removed]
        active.extend(feature for feature in delta.features_added if feature not in active)
    return tuple(active)
