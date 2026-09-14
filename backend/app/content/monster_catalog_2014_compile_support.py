from __future__ import annotations

import logging

from app.combat.legendary_actions import LEGENDARY_ACTION_RESOURCE_ID
from app.combat.legendary_resistance import LEGENDARY_RESISTANCE_RESOURCE_ID
from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.content.monster_catalog_2014_reactive_damage import reactive_melee_damage_2014
from app.content.monster_catalog_2014_sneak_attack import sneak_attack_d6_2014
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
    resources.extend(
        ResourceDefinition(id=action_id, name=action_id.replace("-", " ").title(), max_uses=uses)
        for action_id, uses in source.limited_action_uses.items()
        if action_id not in source.action_recharges
    )
    if source.spellcasting is not None:
        resources.extend(
            ResourceDefinition(
                id=f"spell-slot-{level}", name=f"Level {level} Spell Slots", max_uses=count,
            )
            for level, count in sorted(source.spellcasting.slots.items(), key=lambda item: int(item[0]))
        )
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


def _unique_advantage(specs: list[ConditionalAttackAdvantage]) -> list[ConditionalAttackAdvantage]:
    by_trigger = {spec.trigger: spec for spec in specs}
    return list(by_trigger.values())


def bind_attack_traits_2014(source: CatalogMonster2014, attacks: list[WeaponAttack]) -> list[WeaponAttack]:
    blood_frenzy = ConditionalAttackAdvantage(trigger="target_not_full_hp")
    sneak_attack_d6 = sneak_attack_d6_2014(source.source_traits)
    catalog_attacks = {attack.id: attack for attack in source.attacks}
    bound: list[WeaponAttack] = []
    for attack in attacks:
        update: dict[str, object] = {}
        source_attack = catalog_attacks.get(attack.id)
        advantage = [
            *attack.conditional_attack_advantage,
            *(source_attack.conditional_attack_advantage if source_attack is not None else []),
        ]
        if "Blood Frenzy" in source.trait_names:
            advantage.append(blood_frenzy)
        if advantage:
            update["conditional_attack_advantage"] = _unique_advantage(advantage)
        if sneak_attack_d6:
            update["sneak_attack_eligible"] = True
        if source_attack is not None and source_attack.grapple_target_policy != "normal":
            update["grapple_target_policy"] = source_attack.grapple_target_policy
        if source_attack is not None and source_attack.ongoing_damage_effect is not None:
            update["ongoing_damage_effect"] = source_attack.ongoing_damage_effect
        if source_attack is not None and source_attack.on_hit_save_effect is not None:
            update["on_hit_save_effect"] = source_attack.on_hit_save_effect
        if source_attack is not None and source_attack.on_hit_contested_movement is not None:
            update["on_hit_contested_movement"] = source_attack.on_hit_contested_movement
        if attack.id in source.limited_action_uses and attack.resource_id is None:
            update["resource_id"] = attack.id
            update["resource_cost"] = 1
        bound.append(attack.model_copy(update=update) if update else attack)
    return bound
