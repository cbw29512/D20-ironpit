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
