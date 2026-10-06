from __future__ import annotations

import logging

from app.content.environment_context_reactions import sunlight_sensitivity_2014
from app.content.monster_attack_trait_bindings_2014 import (
    bonus_attack_grants_2014,
    bound_attack_trait_names_2014,
    conditional_attack_advantage_2014,
    supports_blood_frenzy_2014,
    supports_poor_depth_perception_2014,
    supports_reckless_2014,
)
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_damage_absorption import damage_absorptions_from_source
from app.content.monster_heat_traits_2014 import bound_heat_trait_names_2014
from app.content.monster_legendary_resistance_2014 import legendary_resistance_trait_name_2014
from app.content.monster_passive_grants_2014 import (
    aggressive_tactical_grants_2014,
    bound_passive_trait_names_2014,
)
from app.content.monster_progression_trait_bindings_2014 import (
    bound_progression_trait_names_2014,
    martial_advantage_rider_2014,
    progression_features_2014,
    sneak_attack_d6_2014,
    sneak_attack_eligible_2014,
    starting_condition_ids_2014,
    supports_cunning_action_2014,
)
from app.content.monster_regeneration_2014 import supports_regeneration_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_zero_hp_prevention_2014 import bound_zero_hp_trait_names_2014
from app.domain.environment_contexts import EnvironmentContextReaction

logger = logging.getLogger(__name__)

_MAGIC_WEAPONS = "Magic Weapons"
_INNATE_SPELLCASTING = "Innate Spellcasting"
_SUNLIGHT_SENSITIVITY = "Sunlight Sensitivity"


def environment_context_reactions_2014(
    monster: SourceMonster2014,
) -> list[EnvironmentContextReaction]:
    """Bind printed Sunlight Sensitivity to the shared sunlight context reaction."""
    try:
        if _SUNLIGHT_SENSITIVITY not in monster.trait_names:
            return []
        return [sunlight_sensitivity_2014()]
    except Exception:
        logger.exception(
            "Failed to bind 2014 environment-context reactions for %s.",
            monster.name,
        )
        raise


def bound_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Return source traits fully bound to existing universal mechanics."""
    try:
        bound: set[str] = set()
        bound.update(
            action.name
            for action in condition_auras_from_source(monster.source_traits, "2014")
        )
        bound.update(
            rule.source_name
            for rule in damage_absorptions_from_source(
                monster.source_traits,
                {item.lower() for item in monster.damage_immunities},
            )
        )
        bound.update(bound_attack_trait_names_2014(monster))
        bound.update(bound_progression_trait_names_2014(monster))
        bound.update(bound_passive_trait_names_2014(monster))
        bound.update(bound_heat_trait_names_2014(monster))
        bound.update(bound_zero_hp_trait_names_2014(monster))
        if _MAGIC_WEAPONS in monster.trait_names:
            bound.add(_MAGIC_WEAPONS)
        if _INNATE_SPELLCASTING in monster.trait_names:
            from app.content.monster_innate_support_2014 import supports_innate_spellcasting_2014
            if supports_innate_spellcasting_2014(monster):
                bound.add(_INNATE_SPELLCASTING)
        if _SUNLIGHT_SENSITIVITY in monster.trait_names:
            bound.add(_SUNLIGHT_SENSITIVITY)
        if supports_regeneration_2014(monster):
            bound.add("Regeneration")
        resistance = legendary_resistance_trait_name_2014(monster)
        if resistance:
            bound.add(resistance)
        return frozenset(bound)
    except Exception:
        logger.exception("Failed to classify bound 2014 traits for %s.", monster.name)
        raise
