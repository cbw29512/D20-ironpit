from __future__ import annotations

from app.domain.modifiers import ModifierKind


def validate_combat_modifier_payload(modifier) -> None:
    """Reject CombatModifier payloads that do not match their declared kind."""
    die_kind = modifier.kind in {
        ModifierKind.ATTACK_ROLL_BONUS_DIE, ModifierKind.SAVING_THROW_BONUS_DIE,
        ModifierKind.BONUS_DAMAGE,
    }
    if die_kind and (modifier.dice_count < 1 or modifier.dice_size < 2):
        raise ValueError(f"{modifier.kind.value} requires certified dice.")
    if not die_kind and (modifier.dice_count or modifier.dice_size):
        raise ValueError(f"{modifier.kind.value} does not accept dice.")
    if modifier.kind is ModifierKind.ARMOR_CLASS_MINIMUM:
        if modifier.minimum_value < 1 or modifier.flat_bonus:
            raise ValueError("Minimum AC modifiers require a positive minimum and no flat bonus.")
    elif modifier.minimum_value:
        raise ValueError(f"{modifier.kind.value} does not accept a minimum value.")
    damage_type_kinds = {ModifierKind.BONUS_DAMAGE, ModifierKind.WEAPON_DAMAGE_TYPE_CHOICE}
    if modifier.kind in damage_type_kinds and modifier.damage_type is None:
        raise ValueError(f"{modifier.kind.value} requires a damage type.")
    if modifier.kind not in damage_type_kinds and modifier.damage_type is not None:
        raise ValueError(f"{modifier.kind.value} does not accept a damage type.")
    advantage_kinds = {
        ModifierKind.ATTACKS_AGAINST_ADVANTAGE, ModifierKind.ATTACKS_AGAINST_DISADVANTAGE,
        ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE, ModifierKind.D20_TEST_ADVANTAGE,
    }
    if modifier.kind in advantage_kinds and modifier.flat_bonus:
        raise ValueError("Attack roll-mode modifiers do not accept a flat bonus.")
    if modifier.kind is ModifierKind.ATTACK_ROLL_FLAT and modifier.flat_bonus == 0:
        raise ValueError("Flat attack modifiers require a nonzero bonus.")
    if modifier.kind is ModifierKind.WEAPON_DAMAGE_FLAT and modifier.flat_bonus == 0:
        raise ValueError("Flat weapon-damage modifiers require a nonzero bonus.")
    if modifier.kind is ModifierKind.NEXT_INCOMING_ATTACK_ROLL_FLAT and modifier.flat_bonus == 0:
        raise ValueError("Next incoming attack-roll flat modifiers require a nonzero bonus.")
    weapon_scoped_kinds = {
        ModifierKind.ATTACK_ROLL_FLAT,
        ModifierKind.WEAPON_DAMAGE_FLAT,
        ModifierKind.DAMAGE_SOURCE_QUALIFIER,
        ModifierKind.WEAPON_DAMAGE_TYPE_CHOICE,
    }
    if modifier.kind not in weapon_scoped_kinds and modifier.weapon_id is not None:
        raise ValueError(f"{modifier.kind.value} does not accept a weapon id.")
    if modifier.kind is ModifierKind.DAMAGE_SOURCE_QUALIFIER and (
        modifier.weapon_id is None or modifier.source_qualifier is None
    ):
        raise ValueError("Damage source qualifier modifiers require a weapon id and qualifier.")
    if modifier.kind is ModifierKind.WEAPON_DAMAGE_TYPE_CHOICE and modifier.weapon_id is None:
        raise ValueError("Weapon damage-type choice modifiers require a weapon id.")
    if modifier.kind is not ModifierKind.DAMAGE_SOURCE_QUALIFIER and modifier.source_qualifier is not None:
        raise ValueError(f"{modifier.kind.value} does not accept a source qualifier.")
    if modifier.kind in {ModifierKind.SAVING_THROW_FLAT, ModifierKind.COVER_SAVING_THROW_FLAT} and modifier.flat_bonus == 0:
        raise ValueError("Flat saving-throw modifiers require a nonzero bonus.")
    if modifier.kind is ModifierKind.CONDITION_IMMUNITY and modifier.condition_id is None:
        raise ValueError("Condition-immunity modifiers require a condition id.")
    if modifier.kind is not ModifierKind.CONDITION_IMMUNITY and modifier.condition_id is not None:
        raise ValueError(f"{modifier.kind.value} does not accept a condition id.")
    if modifier.kind is ModifierKind.DEBUFF_COUNTER and modifier.debuff_counter is None:
        raise ValueError("Debuff-counter modifiers require a counter definition.")
    if modifier.kind is not ModifierKind.DEBUFF_COUNTER and modifier.debuff_counter is not None:
        raise ValueError(f"{modifier.kind.value} does not accept a debuff counter.")
    if modifier.kind is ModifierKind.ZERO_HP_REPLACEMENT and modifier.replacement_hp < 1:
        raise ValueError("Zero-HP replacement modifiers require positive replacement HP.")
    if modifier.kind is not ModifierKind.ZERO_HP_REPLACEMENT and (
        modifier.replacement_hp or modifier.prevents_instant_death
    ):
        raise ValueError(f"{modifier.kind.value} does not accept zero-HP replacement fields.")
    if modifier.source_creature_types and modifier.kind not in {
        ModifierKind.ATTACKS_AGAINST_DISADVANTAGE, ModifierKind.CONDITION_IMMUNITY,
        ModifierKind.SAVING_THROW_ADVANTAGE, ModifierKind.TARGETING_SAVE_GATE,
    }:
        raise ValueError(f"{modifier.kind.value} does not accept source creature types.")
    if modifier.bypass_attacker_senses and modifier.kind is not ModifierKind.ATTACKS_AGAINST_DISADVANTAGE:
        raise ValueError(f"{modifier.kind.value} does not accept attacker-sense bypass.")
    if len(set(modifier.bypass_attacker_senses)) != len(modifier.bypass_attacker_senses):
        raise ValueError("Attacker-sense bypass values must be unique.")
    if modifier.required_active_effect_ids and modifier.kind is not ModifierKind.CONDITION_IMMUNITY:
        raise ValueError(f"{modifier.kind.value} does not accept active-effect requirements.")
    required_effects = [item.strip().casefold() for item in modifier.required_active_effect_ids]
    if any(not item for item in required_effects) or len(set(required_effects)) != len(required_effects):
        raise ValueError("Active-effect requirements must be non-empty and unique.")
    modifier.required_active_effect_ids = required_effects
    if modifier.kind in {ModifierKind.SAVING_THROW_ADVANTAGE, ModifierKind.TARGETING_SAVE_GATE} and not modifier.save_ability:
        raise ValueError(f"{modifier.kind.value} requires a save ability.")
    if modifier.kind is ModifierKind.TARGETING_SAVE_GATE and modifier.save_dc is None:
        raise ValueError("Targeting save gates require a DC.")
    if modifier.kind is not ModifierKind.TARGETING_SAVE_GATE and modifier.save_dc is not None:
        raise ValueError(f"{modifier.kind.value} does not accept a save DC.")
    if modifier.kind is not ModifierKind.TARGETING_SAVE_GATE and modifier.success_immunity_hours is not None:
        raise ValueError(f"{modifier.kind.value} does not accept targeting-gate success immunity.")
    if modifier.kind not in {
        ModifierKind.SAVING_THROW_ADVANTAGE,
        ModifierKind.SAVING_THROW_FLAT,
        ModifierKind.COVER_SAVING_THROW_FLAT,
        ModifierKind.TARGETING_SAVE_GATE,
    } and modifier.save_ability:
        raise ValueError(f"{modifier.kind.value} does not accept a save ability.")
    if modifier.requires_magical_effect and modifier.kind is not ModifierKind.SAVING_THROW_ADVANTAGE:
        raise ValueError("Only saving-throw Advantage can require a magical-effect context.")
    if modifier.requires_spell_effect and modifier.kind is not ModifierKind.SAVING_THROW_ADVANTAGE:
        raise ValueError("Only saving-throw Advantage can require a spell-effect context.")
    if modifier.required_effect_tags and modifier.kind is not ModifierKind.SAVING_THROW_ADVANTAGE:
        raise ValueError("Only saving-throw Advantage can require effect tags.")
    effect_tags = [item.strip().casefold() for item in modifier.required_effect_tags]
    if any(not item for item in effect_tags) or len(set(effect_tags)) != len(effect_tags):
        raise ValueError("Saving-throw Advantage effect tags must be non-empty and unique.")
    modifier.required_effect_tags = effect_tags
    if modifier.consume_on_attack_against and modifier.kind is not ModifierKind.ATTACKS_AGAINST_ADVANTAGE:
        raise ValueError("Only attack-advantage defender modifiers can be consumed by the next attack.")
    if modifier.consume_on_saving_throw and modifier.kind is not ModifierKind.SAVING_THROW_DISADVANTAGE:
        raise ValueError("Only saving-throw Disadvantage modifiers can be consumed by a saving throw.")
    if modifier.ends_on_owner_attack and modifier.kind is not ModifierKind.TARGETING_SAVE_GATE:
        raise ValueError("Only targeting save gates can end when their owner attacks.")
    if modifier.kind is ModifierKind.SPEED and modifier.flat_bonus == 0:
        raise ValueError("Speed modifiers require a nonzero flat bonus.")
    if modifier.kind is ModifierKind.SPEED_MULTIPLIER:
        if modifier.flat_bonus != 0 or modifier.multiplier == 1.0:
            raise ValueError("Speed multipliers require a non-1 multiplier and no flat bonus.")
    elif modifier.multiplier != 1.0:
        raise ValueError(f"{modifier.kind.value} does not accept a multiplier.")
    if modifier.kind is ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE and modifier.target_id is None:
        raise ValueError("Target-scoped attack Advantage requires a target id.")
