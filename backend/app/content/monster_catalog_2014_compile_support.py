from __future__ import annotations

import logging

from app.combat.legendary_actions import LEGENDARY_ACTION_RESOURCE_ID
from app.combat.legendary_resistance import LEGENDARY_RESISTANCE_RESOURCE_ID
from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.content.monster_catalog_2014_traits import legendary_resistance_uses_2014
from app.domain.character_builds import AbilityScores
from app.domain.combatants import RechargeRule, ResourceDefinition
from app.domain.weapons import ConditionalAttackAdvantage, WeaponAttack

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
    resources = [
        ResourceDefinition(
            id=action_id, name=action_id.replace("-", " ").title(), max_uses=1,
            recharge=RechargeRule(minimum_roll=minimum_roll),
        )
        for action_id, minimum_roll in source.action_recharges.items()
    ]
    uses = legendary_resistance_uses_2014(source.trait_names)
    if uses:
        resources.append(ResourceDefinition(
            id=LEGENDARY_RESISTANCE_RESOURCE_ID,
            name="Legendary Resistance",
            max_uses=uses,
        ))
    if source.legendary_action_uses:
        resources.append(ResourceDefinition(
            id=LEGENDARY_ACTION_RESOURCE_ID,
            name="Legendary Actions",
            max_uses=source.legendary_action_uses,
        ))
    if source.zero_hp_prevention is not None:
        resources.append(ResourceDefinition(
            id=source.zero_hp_prevention.resource_id,
            name="Relentless",
            max_uses=1,
        ))
    return resources


def bind_attack_traits_2014(source: CatalogMonster2014, attacks: list[WeaponAttack]) -> list[WeaponAttack]:
    if "Blood Frenzy" not in source.trait_names:
        return attacks
    advantage = ConditionalAttackAdvantage(trigger="target_not_full_hp")
    return [
        attack.model_copy(update={
            "conditional_attack_advantage": [*attack.conditional_attack_advantage, advantage],
        })
        for attack in attacks
    ]
