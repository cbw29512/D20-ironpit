from __future__ import annotations

import logging

from app.content.monster_legendary_resistance_2014 import (
    RESOURCE_ID as LR_RESOURCE_ID,
    legendary_resistance_uses_from_names,
)
from app.content.monster_regeneration_2024 import regeneration_trait_2024
from app.content.monster_loathsome_limbs_2024 import loathsome_limbs_stack_2024
from app.content.monster_trait_source_audit import source_trait_names
from app.domain.combatants import ResourceDefinition
from app.domain.models import CombatantTemplate
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.save_success_overrides import FailedSaveSuccessOverride

logger = logging.getLogger(__name__)
_MAGIC_RESISTANCE = "Magic Resistance"
def _source_traits(name: str) -> object:
    from app.content.monster_catalog import load_monster_rows
    rows = [row for row in load_monster_rows() if row["name"] == name]
    if len(rows) != 1:
        raise ValueError(f"Expected one SRD 5.2.1 row for {name!r}; found {len(rows)}.")
    return rows[0].get("traits", "")


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
        source_traits = _source_traits(template.name)
        regeneration = regeneration_trait_2024(source_traits)
        limb_stack = loathsome_limbs_stack_2024(source_traits)
        updates: dict[str, object] = {
            "source_trait_names": names,
            "progression_features": features,
            "regeneration": regeneration,
            "triggered_extra_attack_stacks": [limb_stack] if limb_stack is not None else [],
        }
        lr_uses = legendary_resistance_uses_from_names(names, owner=template.name)
        if lr_uses:
            printed = f"Legendary Resistance ({lr_uses}/Day)"
            resources = [item for item in template.resources if item.id != LR_RESOURCE_ID]
            resources.append(ResourceDefinition(id=LR_RESOURCE_ID, name=printed, max_uses=lr_uses))
            overrides = [
                item for item in template.save_success_overrides if item.source_id != LR_RESOURCE_ID
            ]
            overrides.append(FailedSaveSuccessOverride(
                source_id=LR_RESOURCE_ID, source_name=printed, resource_id=LR_RESOURCE_ID,
            ))
            updates["resources"] = resources
            updates["save_success_overrides"] = overrides
        return template.model_copy(update=updates)
    except Exception:
        logger.exception("Failed to bind 2024 source traits for %s.", template.name)
        raise


def bind_monster_source_traits_2024_many(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    return [bind_monster_source_traits_2024(template) for template in templates]
