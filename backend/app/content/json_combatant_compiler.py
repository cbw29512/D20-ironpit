from __future__ import annotations

import json
import logging
from pathlib import Path

from app.domain.capabilities import CombatantDefinition
from app.domain.combatant_source import (
    HeroBuildSource,
    HeroCatalogSource,
    HeroProgressionSource,
    SubclassProgressionSource,
)

LOGGER = logging.getLogger(__name__)


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.exception("Unable to read combatant source JSON path=%s", path)
        raise ValueError(f"Unable to read combatant source JSON: {path}") from exc


def load_hero_build(path: Path) -> HeroBuildSource:
    try:
        return HeroBuildSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero build path=%s", path)
        raise


def load_hero_catalog(path: Path) -> HeroCatalogSource:
    try:
        return HeroCatalogSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero catalog path=%s", path)
        raise


def load_hero_progression(path: Path) -> HeroProgressionSource:
    try:
        return HeroProgressionSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero progression path=%s", path)
        raise


def load_subclass_progression(path: Path) -> SubclassProgressionSource:
    try:
        return SubclassProgressionSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid subclass progression path=%s", path)
        raise


def fold_hero_level(
    progression: HeroProgressionSource,
    subclass: SubclassProgressionSource,
    level: int,
) -> dict[str, object]:
    try:
        if progression.edition != subclass.edition or progression.class_id != subclass.class_id:
            raise ValueError("Class progression and subclass progression must share edition and class.")
        if not 1 <= level <= len(progression.levels):
            raise ValueError(f"Requested level {level} is outside the available progression.")

        state: dict[str, object] = {
            "edition": progression.edition,
            "class_id": progression.class_id,
            "level": level,
            "capabilities": [],
            "arena_ignored": [],
            "resources": {},
        }
        capabilities: list[str] = []
        ignored: list[str] = []
        resources: dict[str, int] = {}
        abilities: dict[str, int] = {}

        for row in progression.levels[:level]:
            dumped = row.model_dump(exclude_none=True)
            for field in ("proficiency_bonus", "max_hp", "attack_count", "weapon_masteries"):
                if field in dumped:
                    state[field] = dumped[field]
            if row.ability_scores:
                abilities.update(row.ability_scores.model_dump(exclude_none=True))
            resources.update(row.resources)
            capabilities = [item for item in capabilities if item not in row.capabilities_removed]
            capabilities.extend(item for item in row.capabilities_added if item not in capabilities)
            ignored.extend(item for item in row.arena_ignored if item not in ignored)

            overlay = subclass.deltas.get(row.level)
            if overlay:
                capabilities = [item for item in capabilities if item not in overlay.capabilities_removed]
                capabilities.extend(item for item in overlay.capabilities_added if item not in capabilities)
                ignored.extend(item for item in overlay.arena_ignored if item not in ignored)

        state["ability_scores"] = abilities
        state["resources"] = resources
        state["capabilities"] = capabilities
        state["arena_ignored"] = ignored
        state["subclass_id"] = subclass.subclass_id
        return state
    except Exception:
        LOGGER.exception(
            "Failed to fold hero progression class=%s subclass=%s level=%s",
            progression.class_id,
            subclass.subclass_id,
            level,
        )
        raise


def _modifier(score: int) -> int:
    return (score - 10) // 2


def compile_hero_definition(
    hero_id: str,
    hero_name: str,
    folded: dict[str, object],
    build: HeroBuildSource,
) -> CombatantDefinition:
    """Compile generic folded hero data into the same definition boundary monsters use."""
    try:
        if folded["edition"] != build.edition or folded["class_id"] != build.class_id:
            raise ValueError("Folded progression and hero build must share edition and class.")
        abilities = dict(folded["ability_scores"])
        proficiency = int(folded["proficiency_bonus"])
        attacks = []
        for attack in build.attacks:
            modifier = _modifier(int(abilities[attack.ability]))
            attacks.append({
                "id": attack.id, "name": attack.name, "weapon_id": attack.weapon_id,
                "attack_kind": attack.attack_kind, "attack_bonus": proficiency + modifier,
                "damage": {"count": attack.dice_count, "size": attack.dice_size, "bonus": modifier},
                "damage_type": attack.damage_type, "animation": attack.animation,
                "reach_ft": attack.reach_ft, "normal_range_ft": attack.normal_range_ft,
                "long_range_ft": attack.long_range_ft, "mastery_property": attack.mastery_property,
                "heavy": attack.heavy, "two_handed": attack.two_handed,
                "attack_ability": attack.ability, "attack_ability_modifier": modifier,
            })
        saves = {
            ability: _modifier(int(score)) + (proficiency if ability in build.save_proficiencies else 0)
            for ability, score in abilities.items()
        }
        skills = {
            skill: _modifier(int(abilities[ability])) + proficiency
            for skill, ability in build.skill_proficiencies.items()
        }
        attack_count = int(folded["attack_count"])
        attack_ids = [attack.id for attack in build.attacks]
        attack_action = None if attack_count == 1 else {
            "id": "extra-attack", "name": "Extra Attack", "is_attack_action": True,
            "slots": [{"attack_ids": attack_ids} for _ in range(attack_count)],
        }
        resources = [
            {"id": resource_id, "name": resource_id.replace("-", " ").title(), "max_uses": uses}
            for resource_id, uses in dict(folded["resources"]).items() if uses > 0
        ]
        return CombatantDefinition.model_validate({
            "schema_version": 1, "id": f"{hero_id}-l{folded['level']}", "name": hero_name,
            "archetype": build.class_id.title(), "level": folded["level"], "kind": "character",
            "ruleset": build.edition, "ability_scores": abilities, "armor_class": build.armor_class,
            "max_hp": folded["max_hp"], "speed_ft": build.speed_ft,
            "initiative_bonus": _modifier(int(abilities["dexterity"])),
            "attacks": attacks, "primary_attack_id": build.primary_attack_id,
            "attack_action": attack_action, "saving_throw_bonuses": saves, "skill_bonuses": skills,
            "fighting_style": build.fighting_style, "weapon_masteries": folded["weapon_masteries"],
            "resources": resources, "visual": build.visual, "source": build.source,
            "unsupported_capabilities": list(folded["arena_ignored"]),
        })
    except Exception:
        LOGGER.exception("Failed to compile hero definition hero=%s level=%s", hero_id, folded.get("level"))
        raise
