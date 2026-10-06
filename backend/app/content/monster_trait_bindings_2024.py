from __future__ import annotations

import logging

from app.content.monster_damage_absorption import damage_absorptions_2024
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_regeneration_2024 import regeneration_trait_2024
from app.content.monster_loathsome_limbs_2024 import loathsome_limbs_stack_2024
from app.content.monster_trait_source_audit import source_trait_names
from app.domain.models import CombatantTemplate
from app.domain.progression import SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_MAGIC_RESISTANCE = "Magic Resistance"
def _source_row(name: str) -> dict[str, object]:
    try:
        from app.content.monster_catalog import load_monster_rows
        rows = [row for row in load_monster_rows() if row["name"] == name]
        if len(rows) != 1:
            raise ValueError(f"Expected one SRD 5.2.1 row for {name!r}; found {len(rows)}.")
        return rows[0]
    except Exception:
        logger.exception("Failed to retrieve 2024 trait source for %s.", name)
        raise


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
        row = _source_row(template.name)
        source_traits = row.get("traits", "")
        regeneration = regeneration_trait_2024(source_traits)
        limb_stack = loathsome_limbs_stack_2024(source_traits)
        auras = condition_auras_from_source(source_traits, "2024")
        aura_ids = {action.id for action in auras}
        return template.model_copy(update={
            "source_trait_names": names,
            "progression_features": features,
            "regeneration": regeneration,
            "damage_absorptions": damage_absorptions_2024(row),
            "timed_self_buff_actions": [
                *[action for action in template.timed_self_buff_actions if action.id not in aura_ids],
                *auras,
            ],
            "triggered_extra_attack_stacks": [limb_stack] if limb_stack is not None else [],
        })
    except Exception:
        logger.exception("Failed to bind 2024 source traits for %s.", template.name)
        raise


def bind_monster_source_traits_2024_many(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    return [bind_monster_source_traits_2024(template) for template in templates]
