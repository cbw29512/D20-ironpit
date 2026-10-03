from __future__ import annotations

from collections.abc import Callable

from app.content.bard_combat_levels import BARD_COMBAT_LEVELS
from app.content.druid_2024_resource_rules import (
    druid_nature_magician_uses,
    druid_wild_resurgence_slot_restore_uses,
    druid_wild_shape_uses,
    land_natural_recovery_free_cast_uses,
)
from app.content.monk_2024_resource_rules import monk_focus_points, uncanny_metabolism_uses
from app.content.level_resources import (
    barbarian_rage_uses,
    cleric_channel_divinity_uses,
    cleric_divine_intervention_uses,
    fighter_action_surge_uses,
    fighter_indomitable_uses,
    fighter_second_wind_uses,
    orc_adrenaline_rush_uses,
)

ResourceRule = tuple[str, str, Callable[[int], int]]


def _bardic_inspiration(level: int) -> int:
    try:
        row = BARD_COMBAT_LEVELS.get(level)
        if row is None:
            raise ValueError("2024 Bard resource progression covers levels 1 through 20.")
        return row.bardic_inspiration_uses
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Failed to resolve 2024 Bardic Inspiration uses for level {level}.") from exc


def _persistent_rage_refresh(level: int) -> int:
    try:
        return 1 if level >= 15 else 0
    except Exception as exc:
        raise ValueError(f"Failed to resolve 2024 Persistent Rage refresh uses for level {level}.") from exc


def _boon_of_fate(level: int) -> int:
    try:
        return 1 if level >= 19 else 0
    except Exception as exc:
        raise ValueError(f"Failed to resolve 2024 Boon of Fate uses for level {level}.") from exc


def _fighter_combat_prowess(level: int) -> int:
    try:
        return 1 if level >= 19 else 0
    except Exception as exc:
        raise ValueError(f"Failed to resolve 2024 Boon of Combat Prowess uses for level {level}.") from exc


def _rogue_stroke(level: int) -> int:
    return 1 if level >= 20 else 0


def _paladins_smite_free_cast(level: int) -> int:
    return 1 if level >= 2 else 0


def _paladin_channel_divinity(level: int) -> int:
    return 2 if level >= 3 else 0


def _berserker_intimidating_presence(level: int) -> int:
    try:
        return 1 if level >= 14 else 0
    except Exception as exc:
        raise ValueError(f"Failed to resolve 2024 Berserker Intimidating Presence uses for level {level}.") from exc


def _open_hand_wholeness_of_body(level: int) -> int:
    try:
        # Kael's canonical Wisdom modifier is +0 at the current level-6 tranche,
        # so RAW's minimum of one use applies. Later ASI changes must update this rule.
        return 1 if level >= 6 else 0
    except Exception as exc:
        raise ValueError(f"Failed to resolve 2024 Wholeness of Body uses for level {level}.") from exc


CLASS_RULES_2024: dict[str, tuple[ResourceRule, ...]] = {
    "barbarian": (
        ("rage", "Rage", barbarian_rage_uses),
        ("persistent-rage-refresh", "Persistent Rage Refresh", _persistent_rage_refresh),
    ),
    "bard": (
        ("bardic-inspiration", "Bardic Inspiration", _bardic_inspiration),
        ("boon-of-fate", "Boon of Fate", _boon_of_fate),
    ),
    "cleric": (
        ("channel-divinity", "Channel Divinity", cleric_channel_divinity_uses),
        ("divine-intervention", "Divine Intervention", cleric_divine_intervention_uses),
        ("boon-of-fate", "Boon of Fate", _boon_of_fate),
    ),
    "fighter": (
        ("second-wind", "Second Wind", fighter_second_wind_uses),
        ("action-surge", "Action Surge", fighter_action_surge_uses),
        ("indomitable", "Indomitable", fighter_indomitable_uses),
        ("boon-combat-prowess", "Boon of Combat Prowess", _fighter_combat_prowess),
    ),
    "druid": (
        ("wild-shape", "Wild Shape", druid_wild_shape_uses),
        (
            "wild-resurgence-slot-restore",
            "Wild Resurgence: Regain Spell Slot",
            druid_wild_resurgence_slot_restore_uses,
        ),
        ("boon-of-fate", "Boon of Fate", _boon_of_fate),
        ("nature-magician-conversion", "Nature Magician", druid_nature_magician_uses),
    ),
    "monk": (
        ("focus-points", "Focus Points", monk_focus_points),
        ("uncanny-metabolism", "Uncanny Metabolism", uncanny_metabolism_uses),
    ),
    "paladin": (
        ("lay-on-hands", "Lay On Hands", lambda level: 5 * level),
        ("paladins-smite-free-cast", "Paladin's Smite: Free Cast", _paladins_smite_free_cast),
        ("channel-divinity", "Channel Divinity", _paladin_channel_divinity),
    ),
    "ranger": (),
    "rogue": (("stroke-of-luck", "Stroke of Luck", _rogue_stroke),),
}

SUBCLASS_RULES_2024: dict[str, tuple[ResourceRule, ...]] = {
    "path-berserker": (
        ("intimidating-presence", "Intimidating Presence", _berserker_intimidating_presence),
    ),
    "warrior-of-the-open-hand": (
        ("wholeness-of-body", "Wholeness of Body", _open_hand_wholeness_of_body),
    ),
    "circle-land": (
        (
            "natural-recovery-free-cast",
            "Natural Recovery: Free Circle Spell",
            land_natural_recovery_free_cast_uses,
        ),
    ),
}

SPECIES_RULES_2024: dict[str, tuple[ResourceRule, ...]] = {
    "orc": (
        ("adrenaline-rush", "Adrenaline Rush", orc_adrenaline_rush_uses),
        ("relentless-endurance", "Relentless Endurance", lambda _level: 1),
    ),
}
