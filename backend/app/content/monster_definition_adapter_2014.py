from __future__ import annotations
from app.content.monster_visual_turn_start_2014 import visual_turn_start_rule_2014
from app.content.monster_visual_disguise_2014 import visual_disguise_action_2014

from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014, source_conditional_attack_advantage_2014
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_opening_initiative_2014 import opening_initiative_damage_source_2014
from app.content.monster_attack_source_corrections_2014 import corrected_attack_range_2014
from app.content.monster_berserk_2014 import berserk_self_buffs_2014
from app.content.monster_basic_candidates_2014 import (
    basic_blockers_2014, modeled_combat_traits_2014, supports_parry_reaction_2014,
)
from app.content.monster_charge_profile_2014 import charge_profile_2014
from app.content.monster_charge_source_corrections_2014 import corrected_charge_profile_2014
from app.content.monster_conditional_damage_defenses_2014 import template_defense_fields_2014
from app.content.monster_healing_2014 import healing_actions_2014, healing_resources_2014
from app.content.monster_heated_body_2014 import heated_body_retaliation_2014, corrosive_form_retaliation_2014
from app.content.monster_grapple_periodic_2014 import supports_grapple_periodic_2014, source_grapple_periodic_proof_2014
from app.content.monster_damage_taken_effects_2014 import damage_taken_timed_effects_2014
from app.content.monster_included_weapon_traits_2014 import weapon_damage_source_qualifiers_2014
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_innate_conditions_2014 import innate_condition_ids_2014
from app.content.monster_grappler_damage_2014 import source_turn_grappler_damage_2014
from app.content.monster_contextual_save_defenses import contextual_save_defenses_2014
from app.content.monster_definition_adapter_support_2014 import (
    ability_values_2014,
    attack_id_2014,
    movement_modes_2014,
    save_bonuses_2014,
)
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.monster_source_invisibility_2014 import source_invisibility_action_2014
from app.content.monster_innate_support_2014 import (
    innate_alternate_spell_casts_2014,
    innate_condition_removal_2014,
    innate_spell_resources_2014,
    innate_timed_self_buffs_2014,
)
from app.content.monster_legendary_bindings_2014 import legendary_action_options_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_core_fields_2014 import monster_core_fields_2014
from app.content.monster_fetid_cloud_2014 import fetid_cloud_zone_2014, fetid_cloud_resources_2014
from app.content.monster_leadership_2014 import leadership_actions_2014, leadership_resources_2014
from app.content.monster_senses_2014 import special_senses_2014, bounded_blindsight_2014
from app.content.monster_spell_slot_resources_2014 import monster_spell_slot_resources_2014
from app.content.monster_multiattack_2014 import multiattack_2014
from app.content.monster_attack_ammunition_2014 import attack_ammunition_2014
from app.content.monster_zero_hp_prevention_2014 import (
    damage_threshold_zero_hp_replacements_2014,
    zero_hp_prevention_resources_2014,
)
from app.content.monster_passive_grants_2014 import aggressive_tactical_grants_2014, conditional_immunity_grants_2014
from app.content.monster_trait_bindings_2014 import (
    bonus_attack_grants_2014, conditional_attack_advantage_2014,
    environment_context_reactions_2014, progression_features_2014, sneak_attack_eligible_2014,
)
from app.content.monster_terminal_effects_2014 import effect_tag_condition_grants_2014, terminal_effect_tags_2014
from app.content.monster_legendary_resistance_2014 import (
    legendary_resistance_override_2014, legendary_resistance_resource_2014,
)
from app.content.movement_modes import standard_arena_closing_speed_from_modes
from app.content.monster_regeneration_2014 import regeneration_trait_2014
from app.content.monster_save_capabilities_2014 import recharge_rules_2014, save_capabilities_2014, save_resources_2014
from app.domain.combatants import ResourceDefinition, VisualLoadout
from app.domain.capabilities import CombatantDefinition
from app.domain.capability_attacks import AttackCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.content.monster_multiattack_variants_2014 import attack_unavailable_reason_2014
from app.domain.character_builds import AbilityScores
from app.domain.reactions import ParryReaction
from app.domain.size import CreatureSize
from app.content.monster_rock_catching_2014 import source_rock_catching_reaction_2014
from app.content.monster_unnerving_mask_2014 import source_unnerving_mask_reaction_2014

def _attack(monster: SourceMonster2014, attack: SourceAttack2014) -> AttackCapabilityDefinition:
    source_grapple_periodic_proof_2014(monster, attack)
    attack = source_completed_mixed_attack_2014(monster, attack)
    printed_attack = next((item for item in monster_core_fields_2014(monster.id).attacks
                           if item.source_id == attack.id), None)
    if printed_attack is None:
        raise ValueError(f"{monster.id} attack {attack.id} is missing from the 327-card registry")
    attack = attack.model_copy(update={
        "on_hit_save_effect": printed_attack.on_hit_save_effect,
        "control_effect": printed_attack.control_effect,
    })
    charge_source = corrected_charge_profile_2014(monster, attack)
    normal_range_ft, long_range_ft = corrected_attack_range_2014(monster, attack)
    kwargs = {
        "id": attack_id_2014(monster, attack.id),
        "weapon_id": attack_id_2014(monster, attack.id),
        "name": attack.name,
        "attack_kind": attack.kind,
        "attack_bonus": printed_attack.attack_bonus,
        "resource_id": attack.id if attack.id in attack_ammunition_2014(monster) else None,
        "attack_ability": attack.attack_ability,
        "sneak_attack_eligible": sneak_attack_eligible_2014(monster, attack),
        "conditional_attack_advantage": [
            *conditional_attack_advantage_2014(monster, attack),
            *source_conditional_attack_advantage_2014(attack),
        ],
        "damage_type": str(printed_attack.damage_type).lower(),
        "animation": "projectile" if attack.kind == "ranged" else "slash",
        "reach_ft": attack.reach_ft,
        "effects": basic_attack_effects_2014(attack, opening_initiative_damage_source_2014(monster)),
        "charge_profile": charge_profile_2014(charge_source, monster_id=monster.id),
        "forbid_target_grappled_by_self": (attack.forbid_target_grappled_by_self and not supports_grapple_periodic_2014(attack)),
        "grapple_target_policy": attack.grapple_target_policy,
        "unavailable_reason": attack_unavailable_reason_2014(monster, attack),
        "damage_source_qualifiers": weapon_damage_source_qualifiers_2014(monster),
    }
    if printed_attack.damage_dice_count:
        kwargs["damage"] = DiceSpec(
            count=printed_attack.damage_dice_count,
            size=printed_attack.damage_dice_size,
            bonus=printed_attack.damage_bonus,
        )
    else:
        kwargs["fixed_damage"] = printed_attack.damage_average
    if attack.kind == "ranged":
        kwargs["normal_range_ft"] = normal_range_ft
        kwargs["long_range_ft"] = long_range_ft
        kwargs["projectile"] = "projectile"
    return AttackCapabilityDefinition(**kwargs)

def adapt_basic_monster_2014(monster: SourceMonster2014) -> CombatantDefinition:
    blockers = basic_blockers_2014(monster)
    if blockers:
        raise ValueError(f"{monster.id} is not a basic 2014 candidate: {', '.join(blockers)}")
    core = monster_core_fields_2014(monster.id)
    scores = AbilityScores(**ability_values_2014(monster))
    movement = movement_modes_2014(monster)
    attacks = [_attack(monster, attack) for attack in monster.attacks]
    blindsight_ft, truesight_ft = special_senses_2014(monster)
    bounded = bounded_blindsight_2014(monster)
    resources = [*save_resources_2014(monster), *fetid_cloud_resources_2014(monster), *leadership_resources_2014(monster)]
    resources.extend(ResourceDefinition(id=key, name=key.replace('-', ' ').title(), max_uses=uses)
                     for key, uses in attack_ammunition_2014(monster).items())
    resources.extend(healing_resources_2014(monster))
    resources.extend(innate_spell_resources_2014(monster))
    resources.extend(monster_spell_slot_resources_2014(monster))
    resources.extend(zero_hp_prevention_resources_2014(monster))
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
    defenses = template_defense_fields_2014(monster)
    defenses["condition_immunities"] = list(core.condition_immunities)
    return CombatantDefinition(
        id=f"2014-{monster.id}", name=monster.name, archetype=f"2014 {monster.creature_type}",
        challenge_rating=monster.challenge_rating, kind="monster", ruleset="2014",
        creature_type=monster.creature_type,
        size=CreatureSize(monster.size.lower()), ability_scores=scores,
        armor_class=core.armor_class, max_hp=core.max_hp, speed_ft=standard_arena_closing_speed_from_modes(movement),
        movement_modes=movement, initiative_bonus=core.initiative_bonus,
        blindsight_ft=blindsight_ft, truesight_ft=truesight_ft,
        blindsight_deafened_ft=bounded[1] if bounded else None,
        blind_beyond_blindsight=bounded is not None,
        blindsight_requires_smell_when_deafened=bounded is not None,
        visual_turn_start_rule=visual_turn_start_rule_2014(monster),
        visual_disguise_action=visual_disguise_action_2014(monster),
        attacks=attacks,
        primary_attack_id=attacks[0].id, attack_action=multiattack_2014(monster),
        save_actions=save_capabilities_2014(monster),
        spell_save_actions=innate_spell_save_actions_2014(monster),
        persistent_save_zone_actions=[zone for zone in [fetid_cloud_zone_2014(monster)] if zone is not None],
        timed_self_buff_actions=[*innate_timed_self_buffs_2014(monster),
            *source_invisibility_action_2014(monster),
            *berserk_self_buffs_2014(monster),
            *heated_body_retaliation_2014(monster),
            *corrosive_form_retaliation_2014(monster),
            *condition_auras_from_source(monster.source_traits, "2014"),
            *contextual_save_defenses_2014(monster)[0], *leadership_actions_2014(monster)],
        healing_actions=healing_actions_2014(monster),
        condition_removal_actions=list(core.condition_removal_actions),
        terminal_effect_tags=terminal_effect_tags_2014(monster),
        effect_tag_condition_grants=effect_tag_condition_grants_2014(monster),
        legendary_actions=legendary_options,
        resources=resources, recharge_rules=recharge_rules_2014(monster),
        regeneration=regeneration_trait_2014(monster),
        damage_taken_timed_effects=damage_taken_timed_effects_2014(monster),
        damage_threshold_zero_hp_replacements=damage_threshold_zero_hp_replacements_2014(monster),
        save_success_overrides=[legendary_override] if legendary_override else [],
        combat_traits=modeled_combat_traits_2014(monster),
        environment_context_reactions=environment_context_reactions_2014(monster),
        progression_features=features, passive_modifier_grants=conditional_immunity_grants_2014(monster),
        bonus_attack_grants=bonus_attack_grants_2014(monster),
        bonus_tactical_action_grants=aggressive_tactical_grants_2014(monster),
        saving_throw_bonuses=dict(core.saving_throw_bonuses),
        skill_bonuses={key.lower(): int(value) for key, value in monster.skills.items()},
        innate_condition_ids=list(core.innate_condition_ids),
        source_allows_hostile_overlap=bool({'Air Form', 'Water Form'} & set(monster.trait_names)),
        source_trait_names=list(monster.trait_names), source_reaction_names=list(monster.reaction_names),
        source_turn_relation_damages=source_turn_grappler_damage_2014(monster),
        source_legendary_action_names=list(monster.legendary_action_names),
        attack_damage_reduction_reaction=source_rock_catching_reaction_2014(monster),
        turn_start_save_condition_reaction=source_unnerving_mask_reaction_2014(monster),
        parry_reaction=ParryReaction(ac_bonus=monster.parry_ac_bonus)
            if supports_parry_reaction_2014(monster) else None,
        **defenses,
        visual=VisualLoadout(armor=monster.creature_type, main_hand=monster.attacks[0].name, body_style=monster.creature_type),
        source=f"SRD 5.1 (2014) {monster.name}",
    )
