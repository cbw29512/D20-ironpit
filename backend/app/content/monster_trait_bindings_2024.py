from __future__ import annotations

import logging

from app.domain.models import CombatantTemplate
from app.domain.progression import SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_MAGIC_RESISTANCE = "Magic Resistance"
_ALL_SAVE_ABILITIES = [
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
]


def bind_monster_traits_2024(template: CombatantTemplate) -> CombatantTemplate:
    """Bind printed 2024 monster traits to existing universal combat primitives."""
    try:
        if template.kind != "monster" or template.ruleset != "2024":
            return template
        if _MAGIC_RESISTANCE not in template.source_trait_names:
            return template

        features = template.progression_features
        grants = list(features.saving_throw_advantage_grants)
        if not any(grant.source_name == _MAGIC_RESISTANCE for grant in grants):
            grants.append(SavingThrowAdvantageGrant(
                source_id="magic-resistance",
                source_name=_MAGIC_RESISTANCE,
                abilities=list(_ALL_SAVE_ABILITIES),
                requires_magical_effect=True,
            ))
        return template.model_copy(update={
            "progression_features": features.model_copy(update={
                "saving_throw_advantage_grants": grants,
            }),
        })
    except Exception:
        logger.exception("Failed to bind 2024 monster traits for %s.", template.name)
        raise


def bind_monster_traits_roster_2024(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    """Apply source-driven 2024 trait bindings across the full monster roster."""
    try:
        return [bind_monster_traits_2024(template) for template in templates]
    except Exception:
        logger.exception("Failed to bind the 2024 monster trait roster.")
        raise
