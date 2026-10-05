from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate
from app.domain.progression import SavingThrowAdvantageGrant
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
_DECLARATIVE_SAVE_TRAITS = frozenset({"Magic Resistance"})
_ALL_SAVE_ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")
_ARENA_NEUTRAL_TRAITS = frozenset({
    "Agile", "Amphibious", "Beast of Burden", "False Appearance", "Flyby", "Hellish Restoration",
    "Hold Breath", "Ice Walk", "Illumination", "Jumper", "Keen Hearing", "Keen Hearing and Sight",
    "Keen Hearing and Smell", "Keen Sight", "Keen Smell", "Limited Amphibiousness", "Mimicry",
    "Earth Glide", "Running Leap", "Shark Telepathy", "Spider Climb", "Standing Leap", "Sunlight Sensitivity",
    "Siege Monster", "Training", "Treasure Sense", "Water Breathing", "Web Walker",
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
    if "Blood Frenzy" in expected:
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        if not attacks or any(
            not any(spec.trigger == "target_not_full_hp" for spec in attack.conditional_attack_advantage)
            for attack in attacks
        ):
            issues.append("trait-runtime-missing:blood-frenzy")
    if "Magic Resistance" in expected:
        grants = template.progression_features.saving_throw_advantage_grants
        if not any(
            grant.source_name == "Magic Resistance"
            and grant.requires_magical_effect
            and set(grant.abilities) == set(_ALL_SAVE_ABILITIES)
            for grant in grants
        ):
            issues.append("trait-runtime-missing:magic-resistance")
    certified = (
        set(_MODELED_TRAITS)
        | set(_DECLARATIVE_ATTACK_TRAITS)
        | set(_DECLARATIVE_SAVE_TRAITS)
        | set(_ARENA_NEUTRAL_TRAITS)
    )
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
            features = template.progression_features.model_copy(deep=True)
            grants = list(features.saving_throw_advantage_grants)
            if "Magic Resistance" in names and not any(
                grant.source_id == "magic-resistance" for grant in grants
            ):
                grants.append(SavingThrowAdvantageGrant(
                    source_id="magic-resistance",
                    source_name="Magic Resistance",
                    abilities=list(_ALL_SAVE_ABILITIES),
                    requires_magical_effect=True,
                ))
                features = features.model_copy(update={"saving_throw_advantage_grants": grants})
            completed.append(template.model_copy(update={
                "source_trait_names": names,
                "progression_features": features,
            }))
        return completed
    except Exception:
        logger.exception("Failed to derive canonical monster trait fingerprints from SRD source.")
        raise
