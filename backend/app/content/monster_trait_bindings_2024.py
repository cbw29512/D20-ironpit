from __future__ import annotations

import logging

from app.content.monster_trait_source_audit import source_trait_names
from app.domain.models import CombatantTemplate
from app.domain.progression import SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_MAGIC_RESISTANCE = "Magic Resistance"
_ALL_SAVE_ABILITIES = (
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
)


def bind_monster_source_traits_2024(template: CombatantTemplate) -> CombatantTemplate:
    """Bind source-printed 2024 monster traits to existing universal primitives."""
    try:
        if template.kind != "monster" or template.ruleset != "2024":
            return template
        names = source_trait_names(template.name)
        features = template.progression_features.model_copy(deep=True)
        grants = [
            grant
            for grant in features.saving_throw_advantage_grants
            if grant.source_id != "magic-resistance"
        ]
        if _MAGIC_RESISTANCE in names:
            grants.append(SavingThrowAdvantageGrant(
                source_id="magic-resistance",
                source_name=_MAGIC_RESISTANCE,
                abilities=list(_ALL_SAVE_ABILITIES),
                requires_magical_effect=True,
            ))
        features.saving_throw_advantage_grants = grants
        return template.model_copy(update={
            "source_trait_names": names,
            "progression_features": features,
        })
    except Exception:
        logger.exception("Failed to bind 2024 source traits for %s.", template.name)
        raise


def bind_monster_source_traits_2024_many(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    return [bind_monster_source_traits_2024(template) for template in templates]
