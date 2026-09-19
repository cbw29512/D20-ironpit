#!/usr/bin/env python3
"""Export edition-scoped hero JSON from certified templates and 2024 class spines."""

from __future__ import annotations

import json
import sys
from dataclasses import fields
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.content.canonical_class_combat_spines import CANONICAL_CLASS_COMBAT_SPINES
from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.subclass_combat_overlays import (
    SUBCLASS_COMBAT_OVERLAYS,
    subclass_feature_ids_for_class,
    subclass_overlay,
)


SKILL_ABILITY = {
    "athletics": "strength", "acrobatics": "dexterity", "sleight-of-hand": "dexterity",
    "stealth": "dexterity", "arcana": "intelligence", "history": "intelligence",
    "investigation": "intelligence", "nature": "intelligence", "religion": "intelligence",
    "animal-handling": "wisdom", "insight": "wisdom", "medicine": "wisdom",
    "perception": "wisdom", "survival": "wisdom", "deception": "charisma",
    "intimidation": "charisma", "performance": "charisma", "persuasion": "charisma",
}
ORC_CAPABILITIES = {"savage-attacker", "adrenaline-rush", "relentless-endurance"}
ABILITY_NAMES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")
HIT_DIE = {
    "barbarian": 12, "fighter": 10, "paladin": 10, "ranger": 10, "bard": 8, "cleric": 8,
    "druid": 8, "monk": 8, "rogue": 8, "warlock": 8, "sorcerer": 6, "wizard": 6,
}


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _row_resources(row: object) -> dict[str, int]:
    resources: dict[str, int] = {}
    mapping = {
        "second_wind_uses": "second-wind",
        "action_surge_uses": "action-surge",
        "indomitable_uses": "indomitable",
        "rage_uses": "rage",
        "focus_points": "ki",
        "channel_divinity_uses": "channel-divinity",
        "lay_on_hands_pool": "lay-on-hands",
        "bardic_inspiration_uses": "bardic-inspiration",
        "wild_shape_uses": "wild-shape",
        "sorcery_points": "sorcery-points",
        "favored_enemy_uses": "hunters-mark",
        "pact_slots": "pact-slot",
    }
    for field, resource_id in mapping.items():
        value = getattr(row, field, None)
        if isinstance(value, int) and value > 0:
            resources[resource_id] = value
    slots = getattr(row, "spell_slots", None)
    if slots:
        for index, uses in enumerate(slots, start=1):
            if uses:
                resources[f"spell-slot-{index}"] = uses
    return resources


def _sparse_levels(rows: dict[int, object], class_id: str) -> list[dict[str, object]]:
    subclass_ids = subclass_feature_ids_for_class(class_id)
    levels = []
    previous_pb = None
    previous_attacks = None
    previous_unarmed = None
    for level in sorted(rows):
        row = rows[level]
        item: dict[str, object] = {"level": level}
        pb = getattr(row, "proficiency_bonus", None)
        if pb is not None and pb != previous_pb:
            item["proficiency_bonus"] = pb
            previous_pb = pb
        attacks = getattr(row, "attack_count", None)
        if attacks is not None and attacks != previous_attacks:
            item["attack_count"] = attacks
            previous_attacks = attacks
        die = getattr(row, "martial_arts_die", None)
        if die is not None and die != previous_unarmed:
            item["unarmed_dice_size"] = die
            previous_unarmed = die
        resources = _row_resources(row)
        if resources:
            item["resources"] = resources
        added = [
            feature for feature in getattr(row, "features_added", ())
            if feature not in ORC_CAPABILITIES and feature not in subclass_ids
        ]
        removed = [
            feature for feature in getattr(row, "features_removed", ())
            if feature not in subclass_ids
        ]
        ignored = list(getattr(row, "arena_ignored", ()))
        if added:
            item["capabilities_added"] = added
        if removed:
            item["capabilities_removed"] = removed
        if ignored:
            item["arena_ignored"] = ignored
        if level == 1 and "attack_count" not in item:
            item["attack_count"] = 1
        if level == 1 and "proficiency_bonus" not in item:
            item["proficiency_bonus"] = 2
        levels.append(item)
    return levels


def export_2024_class_tables(data_root: Path) -> None:
    for class_id, rows in CANONICAL_CLASS_COMBAT_SPINES.items():
        payload = {
            "schema_version": 1,
            "edition": "2024",
            "class_id": class_id,
            "source": f"D&D Beyond Basic Rules 2024: {class_id.title()}",
            "hit_die": HIT_DIE[class_id],
            "levels": _sparse_levels(rows, class_id),
        }
        _write(data_root / "2024" / "class_progressions" / f"{class_id}.json", payload)
        overlay_ids = [
            overlay.subclass_id for overlay in SUBCLASS_COMBAT_OVERLAYS.values()
            if overlay.class_id == class_id
        ]
        for subclass_id in sorted(set(overlay_ids)):
            overlay = subclass_overlay(subclass_id)
            deltas = {
                str(level): {
                    key: list(value)
                    for key, value in {
                        "capabilities_added": delta.features_added,
                        "capabilities_removed": delta.features_removed,
                        "arena_ignored": delta.arena_ignored,
                    }.items()
                    if value
                }
                for level, delta in overlay.deltas.items()
            }
            _write(
                data_root / "2024" / "subclasses" / f"{subclass_id}.json",
                {
                    "schema_version": 1,
                    "edition": "2024",
                    "class_id": class_id,
                    "subclass_id": subclass_id,
                    "deltas": deltas,
                },
            )


def _scores_from_template(template) -> dict[str, int] | None:
    scores = template.ability_scores
    if scores is None:
        return None
    return scores.model_dump()


CLASS_SAVE_PROFICIENCIES = {
    "barbarian": ("strength", "constitution"),
    "bard": ("dexterity", "charisma"),
    "cleric": ("wisdom", "charisma"),
    "druid": ("intelligence", "wisdom"),
    "fighter": ("strength", "constitution"),
    "monk": ("strength", "dexterity"),
    "paladin": ("wisdom", "charisma"),
    "ranger": ("strength", "dexterity"),
    "rogue": ("dexterity", "intelligence"),
    "sorcerer": ("constitution", "charisma"),
    "warlock": ("wisdom", "charisma"),
    "wizard": ("intelligence", "wisdom"),
}


def _scores_from_row(row) -> dict[str, int]:
    scores = {name: 10 for name in ABILITY_NAMES}
    for name in ABILITY_NAMES:
        value = getattr(row, name, None)
        if isinstance(value, int):
            scores[name] = value
    return scores


def _scores_from_saves_and_attack(template, class_id: str) -> dict[str, int] | None:
    saves = template.saving_throw_bonuses or {}
    if not saves:
        return None
    pb = 2 + (template.level - 1) // 4
    trained = CLASS_SAVE_PROFICIENCIES.get(class_id, ())
    scores = {name: 10 for name in ABILITY_NAMES}
    for name in ABILITY_NAMES:
        bonus = saves.get(name)
        if not isinstance(bonus, int):
            continue
        modifier = bonus - pb if name in trained else bonus
        scores[name] = 10 + (2 * modifier)
    if isinstance(template.initiative_bonus, int):
        scores["dexterity"] = 10 + (2 * template.initiative_bonus)
    return scores


def _asi_map(score_rows: list[tuple[int, dict[str, int]]]) -> tuple[dict[str, int], dict[str, dict[str, int]]]:
    base = dict(score_rows[0][1])
    improvements: dict[str, dict[str, int]] = {}
    previous = dict(base)
    for level, scores in score_rows[1:]:
        changed = {key: value for key, value in scores.items() if previous[key] != value}
        if changed:
            improvements[str(level)] = changed
        previous = scores
    return base, improvements


def _masteries_by_level(templates) -> dict[str, list[str]]:
    by_level: dict[str, list[str]] = {}
    previous: list[str] | None = None
    for template in templates:
        current = list(template.weapon_masteries or [])
        if current != previous:
            by_level[str(template.level)] = current
            previous = current
    return by_level


def _styles_by_level(templates) -> dict[str, list[str]]:
    by_level: dict[str, list[str]] = {}
    previous: list[str] | None = None
    for template in templates:
        current = list(template.fighting_styles or ([] if not template.fighting_style else [template.fighting_style]))
        if current != previous:
            by_level[str(template.level)] = current
            previous = current
    return by_level


def _skill_entries(template, scores: dict[str, int], proficiency: int) -> list[dict[str, object]]:
    entries = []
    for skill, bonus in (template.skill_bonuses or {}).items():
        ability = SKILL_ABILITY.get(skill)
        if ability is None:
            continue
        expected_untrained = _modifier(scores[ability])
        entries.append({
            "id": skill,
            "ability": ability,
            "proficient": bonus >= expected_untrained + proficiency,
        })
    return entries


def _save_profs(template, scores: dict[str, int], proficiency: int) -> list[str]:
    profs = []
    for ability, bonus in (template.saving_throw_bonuses or {}).items():
        if bonus >= _modifier(scores[ability]) + proficiency:
            profs.append(ability)
    return profs


def _attack_ability(attack, scores: dict[str, int], proficiency: int) -> str:
    declared = attack.attack_ability
    if declared:
        return declared
    expected = attack.attack_bonus - proficiency
    if expected == _modifier(scores.get("dexterity", 10)):
        return "dexterity"
    if expected == _modifier(scores.get("strength", 10)):
        return "strength"
    return "strength"


def _expertise_by_level(templates, score_rows: list[tuple[int, dict[str, int]]]) -> dict[str, list[str]]:
    by_level: dict[str, list[str]] = {}
    previous: list[str] | None = None
    scores_by_level = {level: scores for level, scores in score_rows}
    for template in templates:
        pb = 2 + (template.level - 1) // 4
        scores = scores_by_level[template.level]
        current = []
        for skill, bonus in (template.skill_bonuses or {}).items():
            ability = SKILL_ABILITY.get(skill)
            if ability is None:
                continue
            if bonus >= _modifier(scores[ability]) + (2 * pb):
                current.append(skill)
        if current != previous:
            by_level[str(template.level)] = current
            previous = current
    return by_level


def _attack_payload(attack, scores: dict[str, int], proficiency: int) -> dict[str, object]:
    weapon = attack.weapon
    payload = {
        "id": attack.id,
        "name": weapon.name,
        "weapon_id": weapon.id,
        "attack_kind": str(getattr(weapon.attack_kind, "value", weapon.attack_kind)),
        "ability": _attack_ability(attack, scores, proficiency),
        "dice_count": weapon.dice_count,
        "dice_size": weapon.dice_size,
        "damage_type": str(getattr(weapon.damage_type, "value", weapon.damage_type)),
        "animation": weapon.animation,
        "reach_ft": weapon.reach_ft,
        "mastery_property": weapon.mastery_property,
        "heavy": weapon.heavy,
        "two_handed": weapon.two_handed,
    }
    if weapon.normal_range_ft:
        payload["normal_range_ft"] = weapon.normal_range_ft
        payload["long_range_ft"] = weapon.long_range_ft
    return payload


def export_certified_track(data_root: Path, progression, templates) -> dict[str, str]:
    first, last = templates[0], templates[-1]
    edition = first.ruleset
    class_id = progression.class_id
    hero = HERO_BY_CLASS[class_id]
    slug = hero.hero_name.lower().replace(" ", "-")
    if edition == "2014":
        slug = f"{slug}-2014"
    species_id = "human" if edition == "2014" else "orc"
    subclass_id = hero.subclass_id
    build_id = f"{slug}-{first.weapon_attack.weapon.id}"
    track_id = f"{slug}-{subclass_id}"
    score_rows = []
    for template in templates:
        dumped = _scores_from_template(template)
        if dumped is None:
            dumped = _scores_from_saves_and_attack(template, class_id)
        if dumped is None and edition == "2024" and class_id in CANONICAL_CLASS_COMBAT_SPINES:
            dumped = _scores_from_row(CANONICAL_CLASS_COMBAT_SPINES[class_id][template.level])
        if dumped is None:
            dumped = {name: 10 for name in ABILITY_NAMES}
        score_rows.append((template.level, dumped))
    base_scores, asis = _asi_map(score_rows)
    origin = [cap for cap in ("savage-attacker",) if cap in [str(item) for item in first.combat_traits]]
    track = {
        "schema_version": 1,
        "edition": edition,
        "id": track_id,
        "hero_id": slug,
        "class_id": class_id,
        "subclass_id": subclass_id,
        "species_id": species_id,
        "build_id": build_id,
        "origin_capabilities": origin,
        "ability_scores": base_scores,
        "ability_score_improvements": asis,
        "hp_by_level": [template.max_hp for template in templates],
        "ac_by_level": [template.armor_class for template in templates],
        "speed_by_level": [template.speed_ft for template in templates],
        "rage_damage_bonus_by_level": [template.rage_damage_bonus for template in templates],
        "weapon_masteries_by_level": _masteries_by_level(templates),
        "fighting_styles_by_level": _styles_by_level(templates),
        "expertise_by_level": _expertise_by_level(templates, score_rows),
    }
    visual = first.visual.model_dump() if first.visual else {
        "armor": "unarmored", "main_hand": first.weapon_attack.weapon.id, "off_hand": None, "body_style": "humanoid"
    }
    attacks = [
        _attack_payload(first.weapon_attack, base_scores, proficiency),
        *(_attack_payload(item, base_scores, proficiency) for item in first.alternate_weapon_attacks),
    ]
    proficiency = 2
    build = {
        "schema_version": 1,
        "edition": edition,
        "id": build_id,
        "class_id": class_id,
        "armor_class": first.armor_class,
        "speed_ft": first.speed_ft,
        "save_proficiencies": _save_profs(first, base_scores, proficiency),
        "skills": _skill_entries(first, base_scores, proficiency),
        "fighting_style": first.fighting_style,
        "attacks": attacks,
        "primary_attack_id": first.weapon_attack.id,
        "visual": visual,
        "source": first.source,
    }
    edition_root = data_root / edition
    _write(edition_root / "tracks" / f"{slug}.json", track)
    _write(edition_root / "builds" / f"{slug}.json", build)
    return {
        "id": slug,
        "name": hero.hero_name,
        "class_id": class_id,
        "subclass_id": subclass_id,
        "build_id": build_id,
        "species": species_id,
        "background": "soldier",
        "track_id": track_id,
        "level_range": [templates[0].level, templates[-1].level],
    }


def export_2014_class_from_templates(data_root: Path, class_id: str, templates, emit_attack_action_at_one: bool) -> None:
    # Build a class table from template resources + known capability ids in progression_features is insufficient.
    # Certified 2014 runtimes encode features in code; write explicit class rows from resource/attack_count changes
    # plus a small capability schedule per class.
    schedules = {
        "fighter": {
            1: {"capabilities_added": ["second-wind"]},
            2: {"capabilities_added": ["action-surge"]},
            5: {"capabilities_added": ["extra-attack"]},
            9: {"capabilities_added": ["indomitable"]},
        },
        "barbarian": {
            1: {"capabilities_added": ["rage"]},
            2: {"capabilities_added": ["reckless-attack", "danger-sense"]},
            5: {"capabilities_added": ["extra-attack", "fast-movement"]},
            11: {"capabilities_added": ["relentless-rage"]},
        },
        "rogue": {
            1: {"capabilities_added": ["sneak-attack"]},
            2: {"capabilities_added": ["cunning-action"]},
            5: {"capabilities_added": ["uncanny-dodge"]},
            7: {"capabilities_added": ["evasion"]},
        },
        "monk": {
            1: {"capabilities_added": ["martial-arts", "unarmored-defense"], "unarmed_dice_size": 4},
            2: {"capabilities_added": ["ki", "unarmored-movement", "flurry-of-blows"]},
            3: {"capabilities_added": ["deflect-missiles"]},
            5: {"capabilities_added": ["extra-attack", "stunning-strike"], "unarmed_dice_size": 6},
            7: {"capabilities_added": ["evasion"]},
        },
        "paladin": {
            1: {"capabilities_added": ["lay-on-hands", "divine-sense"]},
            2: {"capabilities_added": ["divine-smite-2014", "fighting-style"]},
            5: {"capabilities_added": ["extra-attack"]},
            6: {"capabilities_added": ["aura-of-protection-2014"]},
        },
    }
    subclass_schedules = {
        "champion": {
            3: {"capabilities_added": ["improved-critical"]},
            7: {"capabilities_added": ["remarkable-athlete"]},
            15: {"capabilities_added": ["superior-critical"], "capabilities_removed": ["improved-critical"]},
            18: {"capabilities_added": ["survivor"]},
        },
        "path-berserker": {
            3: {"capabilities_added": ["frenzy"]},
            6: {"capabilities_added": ["mindless-rage"]},
        },
        "thief": {3: {"capabilities_added": ["fast-hands", "second-story-work"]}},
        "warrior-open-hand": {3: {"capabilities_added": ["open-hand-technique"]}},
        "oath-devotion": {
            3: {"capabilities_added": ["sacred-weapon-2014", "turn-unholy-2014"]},
            7: {"capabilities_added": ["aura-of-devotion-2014"]},
            10: {"capabilities_added": ["aura-of-courage-2014"]},
        },
    }
    by_level = {template.level: template for template in templates}
    max_level = max(by_level)
    levels = []
    previous_pb = None
    previous_attacks = None
    previous_resources: dict[str, int] = {}
    for level in range(1, max_level + 1):
        template = by_level[level]
        pb = 2 + (level - 1) // 4
        item: dict[str, object] = {"level": level}
        if pb != previous_pb:
            item["proficiency_bonus"] = pb
            previous_pb = pb
        slots = 0 if template.attack_action is None else len(template.attack_action.slots)
        attacks = slots or 1
        if attacks != previous_attacks:
            item["attack_count"] = attacks
            previous_attacks = attacks
        resources = {resource.id: resource.max_uses for resource in template.resources}
        changed = {key: value for key, value in resources.items() if previous_resources.get(key) != value}
        # Keep species-looking resources out of 2014 class tables
        changed = {key: value for key, value in changed.items() if key not in ("adrenaline-rush", "relentless-endurance")}
        if changed:
            item["resources"] = changed
            previous_resources.update(changed)
        extra = schedules.get(class_id, {}).get(level, {})
        item.update(extra)
        if level == 1 and "attack_count" not in item:
            item["attack_count"] = 1
        levels.append(item)
    _write(
        data_root / "2014" / "class_progressions" / f"{class_id}.json",
        {
            "schema_version": 1,
            "edition": "2014",
            "class_id": class_id,
            "source": f"D&D Basic Rules 2014: {class_id.title()}",
            "hit_die": HIT_DIE[class_id],
            "emit_attack_action_at_one": emit_attack_action_at_one,
            "levels": levels,
        },
    )
    subclass_id = HERO_BY_CLASS[class_id].subclass_id
    deltas = {
        str(level): payload
        for level, payload in subclass_schedules.get(subclass_id, {}).items()
        if level <= max_level
    }
    _write(
        data_root / "2014" / "subclasses" / f"{subclass_id}.json",
        {
            "schema_version": 1,
            "edition": "2014",
            "class_id": class_id,
            "subclass_id": subclass_id,
            "deltas": deltas,
        },
    )


def main() -> None:
    data_root = ROOT / "data" / "heroes"
    export_2024_class_tables(data_root)
    _write(
        data_root / "2024" / "species" / "orc.json",
        {
            "schema_version": 1,
            "edition": "2024",
            "id": "orc",
            "speed_ft": 30,
            "capabilities_added": ["adrenaline-rush", "relentless-endurance"],
            "resources": {"relentless-endurance": 1},
            "resource_equals_proficiency": ["adrenaline-rush"],
        },
    )
    _write(
        data_root / "2014" / "species" / "human.json",
        {
            "schema_version": 1,
            "edition": "2014",
            "id": "human",
            "speed_ft": 30,
            "capabilities_added": [],
            "resources": {},
            "resource_equals_proficiency": [],
        },
    )
    catalogs = {"2014": [], "2024": []}
    emit_one = {("2014", "fighter"), ("2014", "barbarian")}
    for progression in CERTIFIED_HERO_PROGRESSIONS:
        templates = [progression.template_builder(level) for level in progression.levels]
        edition = templates[0].ruleset
        identity = export_certified_track(data_root, progression, templates)
        catalogs[edition].append(identity)
        if edition == "2014":
            export_2014_class_from_templates(
                data_root,
                progression.class_id,
                templates,
                emit_attack_action_at_one=(edition, progression.class_id) in emit_one,
            )
    for edition, heroes in catalogs.items():
        _write(
            data_root / edition / "heroes.json",
            {"schema_version": 1, "edition": edition, "heroes": heroes},
        )
    print("exported", {edition: len(heroes) for edition, heroes in catalogs.items()})


if __name__ == "__main__":
    main()
