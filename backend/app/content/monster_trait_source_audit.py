from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.content.monster_legendary_resistance_source import legendary_resistance_trait_issues
from app.content.monster_regeneration_source import regeneration_trait_issues
from app.content.monster_trait_aura_audit import aura_trait_issues
from app.domain.models import CombatantTemplate
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
_CONNECTORS = frozenset({"a", "an", "and", "of", "or", "the", "to"})
_MODELED_TRAITS = {
    "Pack Tactics": CombatTrait.PACK_TACTICS,
    "Bloodied Fury": CombatTrait.BLOODIED_FURY,
    "Bloodied Frenzy": CombatTrait.BLOODIED_FRENZY,
    "Evasion": CombatTrait.EVASION,
    "Swarm": CombatTrait.SWARM,
    "Undead Fortitude": CombatTrait.UNDEAD_FORTITUDE,
}
_DECLARATIVE_ATTACK_TRAITS = frozenset({"Blood Frenzy"})
_ARENA_NEUTRAL_TRAITS = frozenset({
    "Agile", "Amorphous", "Amphibious", "Beast of Burden", "Demonic Restoration", "Diabolical Restoration", "Divine Awareness",
    "Earth Glide", "Eldritch Restoration", "Elemental Restoration", "Exalted Restoration", "False Appearance", "Flyby",
    "Hellish Restoration", "Hold Breath", "Ice Walk", "Illumination", "Inscrutable", "Jumper", "Keen Hearing",
    "Keen Hearing and Sight", "Keen Hearing and Smell", "Keen Sight", "Keen Smell", "Limited Amphibiousness",
    "Mimicry", "Probing Telepathy", "Running Leap", "Sense Magic", "Shark Telepathy", "Siege Monster", "Spider Climb",
    "Standing Leap", "Sunlight Sensitivity", "Sunlight Weakness", "Telepathic Bond", "Training", "Treasure Sense", "Troll Spawn",
    "Tunneler", "Water Breathing", "Web Walker",
})


def _heading_name(value: str) -> str:
    return re.sub(r"\s*\([^)]*\)$", "", value).strip()


def _is_heading(value: str) -> bool:
    if not value or len(value) > 80:
        return False
    plain = _heading_name(value)
    if any(mark in plain for mark in ",:;!?"):
        return False
    words = plain.split()
    if not words:
        return False
    return all(word.lower() in _CONNECTORS or re.fullmatch(r"[A-Z][A-Za-z’'\-]*", word) for word in words)


def parse_trait_names(source_traits: object) -> list[str]:
    text = str(source_traits or "").strip()
    if not text:
        return []
    names: list[str] = []
    for sentence in re.split(r"(?<=\.)\s+", text):
        candidate = sentence[:-1].strip() if sentence.endswith(".") else ""
        if _is_heading(candidate):
            names.append(_heading_name(candidate))
    if not names:
        raise ValueError(f"SRD trait headings could not be parsed from: {text!r}")
    return names


def _movement_trait_issues(template: CombatantTemplate, expected: list[str]) -> list[str]:
    source_has = "Incorporeal Movement" in expected
    runtime_has = template.movement_modes.pass_through_creatures_as_difficult_terrain
    if source_has and not runtime_has:
        return ["trait-runtime-missing:incorporeal-movement"]
    if runtime_has and not source_has:
        return ["trait-source-missing:incorporeal-movement"]
    return []


def _magic_resistance_issues(template: CombatantTemplate, expected: list[str]) -> list[str]:
    source_has = "Magic Resistance" in expected
    if source_has and not template.magic_resistance:
        return ["trait-runtime-missing:magic-resistance"]
    if template.magic_resistance and not source_has:
        return ["trait-source-missing:magic-resistance"]
    return []


def trait_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    expected = parse_trait_names(row.get("traits", ""))
    issues: list[str] = []
    if template.source_trait_names != expected:
        issues.append("source-trait-fingerprint-mismatch")
    for source_name, runtime_trait in _MODELED_TRAITS.items():
        source_has = source_name in expected
        runtime_has = runtime_trait in template.combat_traits
        if source_has and not runtime_has:
            issues.append(f"trait-runtime-missing:{runtime_trait.value}")
        elif runtime_has and not source_has:
            issues.append(f"trait-source-missing:{runtime_trait.value}")
    issues.extend(_movement_trait_issues(template, expected))
    issues.extend(_magic_resistance_issues(template, expected))
    issues.extend(regeneration_trait_issues(template, row))
    legendary_issues, legendary_certified = legendary_resistance_trait_issues(template, expected)
    issues.extend(legendary_issues)
    aura_issues, aura_certified = aura_trait_issues(template, row, expected)
    issues.extend(aura_issues)
    certified = set(_MODELED_TRAITS) | set(_DECLARATIVE_ATTACK_TRAITS) | set(_ARENA_NEUTRAL_TRAITS) | {"Incorporeal Movement", "Magic Resistance", "Regeneration"} | aura_certified
    if legendary_certified:
        certified.add("Legendary Resistance")
    for name in expected:
        if name not in certified:
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            issues.append(f"uncertified-trait:{slug}")
    return issues


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_trait_names(name: str) -> list[str]:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return parse_trait_names(row.get("traits", ""))


def complete_monster_trait_fingerprints(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        completed: list[CombatantTemplate] = []
        for template in templates:
            if template.kind != "monster":
                completed.append(template)
                continue
            names = source_trait_names(template.name)
            traits = list(template.combat_traits)
            for source_name, runtime_trait in _MODELED_TRAITS.items():
                if source_name in names and runtime_trait not in traits:
                    traits.append(runtime_trait)
            completed.append(template.model_copy(update={
                "source_trait_names": names,
                "combat_traits": traits,
                "magic_resistance": "Magic Resistance" in names,
            }))
        return completed
    except Exception as exc:
        logger.exception("Failed to derive canonical monster trait fingerprints from SRD source.")
        raise RuntimeError("Monster trait fingerprints could not be completed.") from exc
