from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.content.monster_regeneration_2024 import regeneration_trait_2024
from app.domain.models import CombatantTemplate
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
_CONNECTORS = frozenset({"a", "an", "and", "of", "or", "the", "to"})
_MODELED_TRAITS = {
    "Pack Tactics": CombatTrait.PACK_TACTICS,
    "Bloodied Fury": CombatTrait.BLOODIED_FURY,
    "Swarm": CombatTrait.SWARM,
    "Undead Fortitude": CombatTrait.UNDEAD_FORTITUDE,
}
_DECLARATIVE_ATTACK_TRAITS = frozenset({"Blood Frenzy"})
_DECLARATIVE_TEMPLATE_TRAITS = frozenset({"Loathsome Limbs", "Magic Resistance", "Regeneration"})
_ARENA_NEUTRAL_TRAITS = frozenset({
    "Agile", "Amphibious", "Beast of Burden", "False Appearance", "Flyby", "Hellish Restoration",
    "Hold Breath", "Ice Walk", "Illumination", "Jumper", "Keen Hearing", "Keen Hearing and Sight",
    "Keen Hearing and Smell", "Keen Sight", "Keen Smell", "Limited Amphibiousness", "Mimicry",
    "Earth Glide", "Running Leap", "Shark Telepathy", "Spider Climb", "Standing Leap", "Sunlight Sensitivity",
    "Siege Monster", "Training", "Treasure Sense", "Troll Spawn", "Water Breathing", "Web Walker",
})


def _is_heading(value: str) -> bool:
    if not value or len(value) > 80 or any(mark in value for mark in ",:;!?"):
        return False
    plain = re.sub(r"\s*\([^)]*\)$", "", value).strip()
    words = plain.split()
    if not words:
        return False
    for word in words:
        if word.lower() in _CONNECTORS:
            continue
        if not re.fullmatch(r"[A-Z][A-Za-z’'\-]*", word):
            return False
    return True


def parse_trait_names(source_traits: object) -> list[str]:
    text = str(source_traits or "").strip()
    if not text:
        return []
    names: list[str] = []
    for sentence in re.split(r"(?<=\.)\s+", text):
        candidate = sentence[:-1].strip() if sentence.endswith(".") else ""
        if _is_heading(candidate):
            names.append(candidate)
    if not names:
        raise ValueError(f"SRD trait headings could not be parsed from: {text!r}")
    return names


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
    if "Magic Resistance" in expected:
        grants = template.progression_features.saving_throw_advantage_grants
        matching = [grant for grant in grants if grant.source_id == "magic-resistance"]
        if len(matching) != 1 or not matching[0].requires_magical_effect or set(matching[0].abilities) != {
            "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"
        }:
            issues.append("trait-runtime-missing:magic-resistance")
    elif any(grant.source_id == "magic-resistance" for grant in template.progression_features.saving_throw_advantage_grants):
        issues.append("trait-source-missing:magic-resistance")
    expected_regeneration = regeneration_trait_2024(row.get("traits", ""))
    if expected_regeneration is not None:
        if template.regeneration is None:
            issues.append("trait-runtime-missing:regeneration")
        elif template.regeneration != expected_regeneration:
            issues.append("trait-runtime-mismatch:regeneration")
    elif template.regeneration is not None:
        issues.append("trait-source-missing:regeneration")
    if "Loathsome Limbs" in expected:
        matches = [
            item for item in template.triggered_extra_attack_stacks
            if item.source_id == "loathsome-limbs"
        ]
        if len(matches) != 1:
            issues.append("trait-runtime-missing:loathsome-limbs")
        else:
            item = matches[0]
            if (
                item.trigger_damage_type.value != "slashing"
                or item.trigger_damage_minimum != 15
                or not item.requires_bloodied
                or item.max_stacks != 4
                or item.max_uses != 4
                or item.exhaustion_per_stack != 1
                or not item.clears_on_regeneration_heal
            ):
                issues.append("trait-runtime-mismatch:loathsome-limbs")
    elif any(item.source_id == "loathsome-limbs" for item in template.triggered_extra_attack_stacks):
        issues.append("trait-source-missing:loathsome-limbs")
    if "Blood Frenzy" in expected:
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        if not attacks or any(
            not any(spec.trigger == "target_not_full_hp" for spec in attack.conditional_attack_advantage)
            for attack in attacks
        ):
            issues.append("trait-runtime-missing:blood-frenzy")
    certified = set(_MODELED_TRAITS) | set(_DECLARATIVE_ATTACK_TRAITS) | set(_DECLARATIVE_TEMPLATE_TRAITS) | set(_ARENA_NEUTRAL_TRAITS)
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
        return [
            template.model_copy(update={"source_trait_names": source_trait_names(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception:
        logger.exception("Failed to derive canonical monster trait fingerprints from SRD source.")
        raise
