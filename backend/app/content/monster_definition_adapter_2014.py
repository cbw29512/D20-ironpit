from __future__ import annotations

from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014
from app.content.monster_basic_candidates_2014 import (
    basic_blockers_2014, modeled_combat_traits_2014, supports_parry_reaction_2014,
)
from app.content.monster_charge_profile_2014 import charge_profile_2014
from app.content.monster_charge_source_corrections_2014 import corrected_charge_profile_2014
from app.content.monster_healing_2014 import healing_actions_2014, healing_resources_2014
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_innate_support_2014 import (
    innate_alternate_spell_casts_2014,
    innate_condition_removal_2014,
    innate_spell_resources_2014,
    innate_timed_self_buffs_2014,
)
from app.content.monster_legendary_bindings_2014 import legendary_action_options_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_trait_bindings_2014 import (
    aggressive_tactical_grants_2014, conditional_attack_advantage_2014,
    environment_context_reactions_2014, progression_features_2014, sneak_attack_eligible_2014,
)
from app.content.monster_legendary_resistance_2014 import (
    legendary_resistance_override_2014,
    legendary_resistance_resource_2014,
)
from app.content.movement_modes import standard_arena_closing_speed_from_modes
from app.content.monster_regeneration_2014 import regeneration_trait_2014
from app.content.monster_save_capabilities_2014 import (
    recharge_rules_2014, save_capabilities_2014, save_resources_2014,
)
from app.domain.combatants import ResourceDefinition, VisualLoadout
from app.domain.weapons import DamageSourceQualifier
from app.domain.capabilities import CombatantDefinition
from app.domain.capability_attacks import (
    AttackCapabilityDefinition,
    CapabilityActionSlot,
    MultiattackCapabilityDefinition,
)
from app.domain.capability_effects import DiceSpec
from app.domain.character_builds import AbilityScores
from app.domain.movement import MovementModes
from app.domain.reactions import ParryReaction
from app.domain.size import CreatureSize

_ABILITY_KEYS = {
    "str": "strength", "dex": "dexterity", "con": "constitution",
    "int": "intelligence", "wis": "wisdom", "cha": "charisma",
}
_FULL_ABILITIES = tuple(_ABILITY_KEYS.values())


def _ability_values(monster: SourceMonster2014) -> dict[str, int]:
    normalized = {_ABILITY_KEYS.get(key.lower(), key.lower()): value for key, value in monster.abilities.items()}
    missing = set(_FULL_ABILITIES) - set(normalized)
    if missing:
        raise ValueError(f"{monster.id} is missing ability scores: {sorted(missing)}")
    return {name: int(normalized[name]) for name in _FULL_ABILITIES}


def _save_bonuses(monster: SourceMonster2014, scores: AbilityScores) -> dict[str, int]:
    bonuses = {name: scores.modifier(name) for name in _FULL_ABILITIES}
    for key, value in monster.saving_throws.items():
        name = _ABILITY_KEYS.get(key.lower(), key.lower())
        if name not in bonuses:
            raise ValueError(f"{monster.id} has unknown saving throw ability {key!r}")
        bonuses[name] = int(value)
    return bonuses


def _movement(monster: SourceMonster2014) -> MovementModes:
    speed = {key.lower().replace("_ft", ""): int(value) for key, value in monster.speed.items()}
    return MovementModes(
        walk_ft=speed.get("walk", speed.get("speed", 0)),
        fly_ft=speed.get("fly", 0),
        climb_ft=speed.get("climb", 0),
        swim_ft=speed.get("swim", 0),
        burrow_ft=speed.get("burrow", 0),
    )


def _attack_id(monster: SourceMonster2014, attack: SourceAttack2014) -> str:
    return f"2014-{monster.id}-{attack.id}".replace("--", "-")


def _attack(monster: SourceMonster2014, attack: SourceAttack2014) -> AttackCapabilityDefinition:
    charge_source = corrected_charge_profile_2014(monster, attack)
    kwargs = {
        "id": _attack_id(monster, attack),
        "weapon_id": _attack_id(monster, attack),
        "name": attack.name,
        "attack_kind": attack.kind,
        "attack_bonus": attack.attack_bonus,
        "attack_ability": attack.attack_ability,
        "sneak_attack_eligible": sneak_attack_eligible_2014(monster, attack),
        "conditional_attack_advantage": conditional_attack_advantage_2014(monster, attack),
        "damage_type": str(attack.damage.type).lower(),
        "animation": "projectile" if attack.kind == "ranged" else "slash",
        "reach_ft": attack.reach_ft,
        "effects": basic_attack_effects_2014(attack),
        "charge_profile": charge_profile_2014(charge_source, monster_id=monster.id),
        "forbid_target_grappled_by_self": attack.forbid_target_grappled_by_self,
        "damage_source_qualifiers": (
            [DamageSourceQualifier.MAGICAL] if "Magic Weapons" in monster.trait_names else []
        ),
    }
    if attack.damage.dice_count:
        kwargs["damage"] = DiceSpec(
            count=attack.damage.dice_count,
            size=attack.damage.dice_size,
            bonus=attack.damage.bonus,
        )
    else:
        kwargs["fixed_damage"] = attack.damage.average
    if attack.kind == "ranged":
        kwargs["normal_range_ft"] = attack.normal_range_ft
        kwargs["long_range_ft"] = attack.long_range_ft
        kwargs["projectile"] = "projectile"
    return AttackCapabilityDefinition(**kwargs)


def _multiattack(monster: SourceMonster2014) -> MultiattackCapabilityDefinition | None:
    if not monster.multiattack_slots:
        return None
    attack_by_source = {attack.id: _attack_id(monster, attack) for attack in monster.attacks}
    return MultiattackCapabilityDefinition(
        id=f"2014-{monster.id}-multiattack",
        name="Multiattack",
        is_attack_action=True,
        slots=[CapabilityActionSlot(attack_ids=[attack_by_source[slot[0]]]) for slot in monster.multiattack_slots],
    )


def adapt_basic_monster_2014(monster: SourceMonster2014) -> CombatantDefinition:
    blockers = basic_blockers_2014(monster)
    if blockers:
        raise ValueError(f"{monster.id} is not a basic 2014 candidate: {', '.join(blockers)}")
    scores = AbilityScores(**_ability_values(monster))
    movement = _movement(monster)
    attacks = [_attack(monster, attack) for attack in monster.attacks]
    resources = list(save_resources_2014(monster))
    resources.extend(healing_resources_2014(monster))
    resources.extend(innate_spell_resources_2014(monster))
    legendary_resource = legendary_resistance_resource_2014(monster)
    if legendary_resource is not None:
        resources.append(legendary_resource)
    legendary_options = legendary_action_options_2014(monster)
    if legendary_options:
        resources.append(ResourceDefinition(
            id="legendary-actions", name="Legendary Actions", max_uses=max(1, monster.legendary_action_uses),
        ))
    legendary_override = legendary_resistance_override_2014(monster)
    features = progression_features_2014(monster)
    feature_update: dict[str, object] = {}
    if legendary_options:
        feature_update["start_turn_resource_refill_ids"] = [
            *features.start_turn_resource_refill_ids,
            "legendary-actions",
        ]
    innate_grants = innate_alternate_spell_casts_2014(monster)
    if innate_grants:
        feature_update["alternate_spell_cast_grants"] = [
            *features.alternate_spell_cast_grants,
            *innate_grants,
        ]
    if feature_update:
        features = features.model_copy(update=feature_update)
    return CombatantDefinition(
        id=f"2014-{monster.id}", name=monster.name, archetype=f"2014 {monster.creature_type}",
        challenge_rating=monster.challenge_rating, kind="monster", ruleset="2014",
        creature_type=monster.creature_type,
        size=CreatureSize(monster.size.lower()), ability_scores=scores,
        armor_class=monster.armor_class, max_hp=monster.max_hp, speed_ft=standard_arena_closing_speed_from_modes(movement),
        movement_modes=movement, initiative_bonus=scores.modifier("dexterity"), attacks=attacks,
        primary_attack_id=attacks[0].id, attack_action=_multiattack(monster),
        save_actions=save_capabilities_2014(monster),
        spell_save_actions=innate_spell_save_actions_2014(monster),
        timed_self_buff_actions=innate_timed_self_buffs_2014(monster),
        healing_actions=healing_actions_2014(monster),
        condition_removal_actions=innate_condition_removal_2014(monster),
        legendary_actions=legendary_options,
        resources=resources, recharge_rules=recharge_rules_2014(monster),
        regeneration=regeneration_trait_2014(monster),
        save_success_overrides=[legendary_override] if legendary_override else [],
        combat_traits=modeled_combat_traits_2014(monster),
        environment_context_reactions=environment_context_reactions_2014(monster),
        progression_features=features, bonus_tactical_action_grants=aggressive_tactical_grants_2014(monster),
        saving_throw_bonuses=_save_bonuses(monster, scores),
        skill_bonuses={key.lower(): int(value) for key, value in monster.skills.items()},
        source_trait_names=list(monster.trait_names), source_reaction_names=list(monster.reaction_names),
        source_legendary_action_names=list(monster.legendary_action_names),
        parry_reaction=ParryReaction(ac_bonus=monster.parry_ac_bonus)
            if supports_parry_reaction_2014(monster) else None,
        damage_resistances=[item.lower() for item in monster.damage_resistances],
        damage_vulnerabilities=[item.lower() for item in monster.damage_vulnerabilities],
        damage_immunities=[item.lower() for item in monster.damage_immunities],
        condition_immunities=[item.lower() for item in monster.condition_immunities],
        visual=VisualLoadout(armor=monster.creature_type, main_hand=monster.attacks[0].name, body_style=monster.creature_type),
        source=f"SRD 5.1 (2014) {monster.name}",
    )