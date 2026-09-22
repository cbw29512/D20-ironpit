from __future__ import annotations

from collections.abc import Iterable

from app.domain.character_builds import AbilityName
from app.domain.progression import ProgressionCombatFeatures


def saving_throw_proficiencies(
    base: Iterable[AbilityName],
    features: ProgressionCombatFeatures,
) -> tuple[AbilityName, ...]:
    """Merge base save proficiencies with source-tagged progression grants."""
    ordered = list(base)
    for grant in features.saving_throw_proficiency_grants:
        for ability in grant.abilities:
            if ability not in ordered:
                ordered.append(ability)
    return tuple(ordered)
