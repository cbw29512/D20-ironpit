from __future__ import annotations

import logging

from app.combat.legendary_resistance import LEGENDARY_RESISTANCE_RESOURCE_ID
from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.content.monster_catalog_2014_traits import legendary_resistance_uses_2014
from app.domain.character_builds import AbilityScores
from app.domain.models import ResourceDefinition

logger = logging.getLogger(__name__)
ABILITY_NAMES = {
    "str": "strength", "dex": "dexterity", "con": "constitution",
    "int": "intelligence", "wis": "wisdom", "cha": "charisma",
}


def ability_scores_2014(source: CatalogMonster2014) -> AbilityScores:
    try:
        return AbilityScores(**{name: source.abilities[key] for key, name in ABILITY_NAMES.items()})
    except Exception as exc:
        logger.exception("Invalid 2014 ability scores for %s.", source.id)
        raise RuntimeError(f"2014 monster {source.id} has invalid ability scores.") from exc


def saving_throw_bonuses_2014(source: CatalogMonster2014) -> dict[str, int]:
    bonuses = {full: (source.abilities[short] - 10) // 2 for short, full in ABILITY_NAMES.items()}
    for key, value in source.saving_throws.items():
        bonuses[ABILITY_NAMES.get(key, key)] = value
    return bonuses


def resources_2014(source: CatalogMonster2014) -> list[ResourceDefinition]:
    uses = legendary_resistance_uses_2014(source.trait_names)
    if not uses:
        return []
    return [
        ResourceDefinition(
            id=LEGENDARY_RESISTANCE_RESOURCE_ID,
            name="Legendary Resistance",
            max_uses=uses,
        )
    ]
