from __future__ import annotations

import logging

from app.content.json_hero_derived import derive_hit_points, require_matching_fingerprint
from app.domain.combatant_source import (
    HeroProgressionSource,
    HeroTrackSource,
    SpeciesSource,
    SubclassProgressionSource,
)

LOGGER = logging.getLogger(__name__)


def fold_hero_level(
    progression: HeroProgressionSource,
    subclass: SubclassProgressionSource,
    species: SpeciesSource,
    track: HeroTrackSource,
    level: int,
) -> dict[str, object]:
    try:
        if progression.edition != subclass.edition or progression.class_id != subclass.class_id:
            raise ValueError("Class progression and subclass progression must share edition and class.")
        if (
            track.edition != progression.edition
            or track.class_id != progression.class_id
            or track.subclass_id != subclass.subclass_id
        ):
            raise ValueError("Hero track must share edition, class, and subclass with the progression files.")
        if species.edition != track.edition or species.id != track.species_id:
            raise ValueError("Species must share edition and id with the hero track.")
        if not 1 <= level <= len(progression.levels):
            raise ValueError(f"Requested level {level} is outside the available progression.")

        capabilities: list[str] = list(species.capabilities_added)
        for item in track.origin_capabilities:
            if item not in capabilities:
                capabilities.append(item)
        ignored: list[str] = []
        resources: dict[str, int] = dict(species.resources)
        abilities = track.ability_scores.model_dump()
        proficiency = 2
        attack_count = 1
        masteries: list[str] = []
        unarmed_dice_size: int | None = None
        fighting_styles: list[str] = []
        expertise: list[str] = []

        for row in progression.levels[:level]:
            dumped = row.model_dump(exclude_none=True)
            if "proficiency_bonus" in dumped:
                proficiency = int(dumped["proficiency_bonus"])
            if "attack_count" in dumped:
                attack_count = int(dumped["attack_count"])
            if "unarmed_dice_size" in dumped:
                unarmed_dice_size = int(dumped["unarmed_dice_size"])
            resources.update(row.resources)
            capabilities = [item for item in capabilities if item not in row.capabilities_removed]
            capabilities.extend(item for item in row.capabilities_added if item not in capabilities)
            ignored.extend(item for item in row.arena_ignored if item not in ignored)

            overlay = subclass.deltas.get(row.level)
            if overlay:
                capabilities = [item for item in capabilities if item not in overlay.capabilities_removed]
                capabilities.extend(item for item in overlay.capabilities_added if item not in capabilities)
                ignored.extend(item for item in overlay.arena_ignored if item not in ignored)

            asi = track.ability_score_improvements.get(row.level)
            if asi:
                abilities.update({key: value for key, value in asi.model_dump().items() if value is not None})
            picked = track.weapon_masteries_by_level.get(row.level)
            if picked is not None:
                masteries = list(picked)
            styles = track.fighting_styles_by_level.get(row.level)
            if styles is not None:
                fighting_styles = list(styles)
            picked_expertise = track.expertise_by_level.get(row.level)
            if picked_expertise is not None:
                expertise = list(picked_expertise)

        for resource_id in species.resource_equals_proficiency:
            resources[resource_id] = proficiency

        max_hp = require_matching_fingerprint(
            "max_hp",
            derive_hit_points(level, progression.hit_die, int(abilities["constitution"])),
            track.hp_by_level[level - 1] if level <= len(track.hp_by_level) else None,
        )
        speed_ft = track.speed_by_level[level - 1] if len(track.speed_by_level) >= level else species.speed_ft
        rage_bonus = (
            track.rage_damage_bonus_by_level[level - 1]
            if len(track.rage_damage_bonus_by_level) >= level else 0
        )
        return {
            "edition": progression.edition,
            "class_id": progression.class_id,
            "subclass_id": subclass.subclass_id,
            "species_id": species.id,
            "level": level,
            "proficiency_bonus": proficiency,
            "max_hp": max_hp,
            "armor_class_fingerprint": (
                track.ac_by_level[level - 1] if len(track.ac_by_level) >= level else None
            ),
            "speed_ft": speed_ft,
            "rage_damage_bonus": rage_bonus,
            "attack_count": attack_count,
            "unarmed_dice_size": unarmed_dice_size,
            "emit_attack_action_at_one": progression.emit_attack_action_at_one,
            "weapon_masteries": masteries,
            "fighting_styles": fighting_styles,
            "expertise": expertise,
            "ability_scores": abilities,
            "resources": resources,
            "capabilities": capabilities,
            "arena_ignored": ignored,
            "unarmored_defense_abilities": list(progression.unarmored_defense_abilities),
            "unarmored_defense_allows_shield": progression.unarmored_defense_allows_shield,
        }
    except Exception:
        LOGGER.exception(
            "Failed to fold hero progression class=%s subclass=%s species=%s level=%s",
            progression.class_id, subclass.subclass_id, species.id, level,
        )
        raise
