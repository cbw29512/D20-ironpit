from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.domain.character_builds import (
    AbilityIncrease,
    AbilityScores,
    FeatureAudit,
)

logger = logging.getLogger(__name__)


def bard_feature_audit(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat_relevant: bool,
    automated: bool,
    runtime_attack_weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    try:
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=feature_name,
            source_reference="D&D Beyond Basic Rules 2024: Bard",
            category=category,
            combat_relevant=combat_relevant,
            automated=automated,
            runtime_attack_weapon_id=runtime_attack_weapon_id,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2024 Bard feature audit for %s.", feature_id)
        raise


def bard_ability_scores(
    level: int,
) -> tuple[AbilityScores, list, list[AbilityIncrease], AbilityScores]:
    try:
        base = canonical_base_ability_scores("bard")
        allowed = ["intelligence", "wisdom", "charisma"]
        background = canonical_background_increases("bard", allowed)
        advancement: list[AbilityIncrease] = []
        if level >= 4:
            advancement.append(AbilityIncrease(ability="charisma", amount=2))
        if level >= 8:
            advancement.extend([
                AbilityIncrease(ability="charisma", amount=1),
                AbilityIncrease(ability="wisdom", amount=1),
            ])
        values = base.model_dump()
        for increase in [*background, *advancement]:
            values[increase.ability] += increase.amount
        return base, background, advancement, AbilityScores(**values)
    except Exception:
        logger.exception("Failed to compile 2024 Bard ability scores at level %s.", level)
        raise


def bard_source_references(level: int) -> list[str]:
    try:
        refs = [
            "D&D Beyond Basic Rules 2024: Bard — Core Traits, Bardic Inspiration, Spellcasting",
            "D&D Beyond Basic Rules 2024: Acolyte background",
            "D&D Beyond Basic Rules 2024: Orc species",
            "D&D Beyond Basic Rules 2024: Studded Leather Armor and Dagger",
        ]
        if level >= 2:
            refs.append("D&D Beyond Basic Rules 2024: Bard 2 — Expertise, Jack of All Trades")
        if level >= 3:
            refs.append("D&D Beyond Basic Rules 2024: College of Lore 3 — Bonus Proficiencies, Cutting Words")
        if level >= 4:
            refs.append("D&D Beyond Basic Rules 2024: Bard 4 — Ability Score Improvement")
        if level >= 5:
            refs.append("D&D Beyond Basic Rules 2024: Bard 5 — Font of Inspiration")
        if level >= 6:
            refs.append("D&D Beyond Basic Rules 2024: College of Lore 6 — Magical Discoveries")
        if level >= 7:
            refs.append("D&D Beyond Basic Rules 2024: Bard 7 — Countercharm")
        if level >= 8:
            refs.append("D&D Beyond Basic Rules 2024: Bard 8 — Ability Score Improvement")
        if level >= 9:
            refs.append("D&D Beyond Basic Rules 2024: Bard 9 — Expertise, level 5 spells")
        if level >= 10:
            refs.append("D&D Beyond Basic Rules 2024: Bard 10 — Magical Secrets")
        if level >= 11:
            refs.append("D&D Beyond Basic Rules 2024: Bard 11 — level 6 spells")
        return refs
    except Exception:
        logger.exception("Failed to compile 2024 Bard source references at level %s.", level)
        raise
