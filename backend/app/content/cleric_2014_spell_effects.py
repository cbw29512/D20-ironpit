from __future__ import annotations

from app.content.cleric_life_domain import disciple_of_life_bonus
from app.content.offensive_spell_effects import build_guiding_bolt, build_sacred_flame
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.domain.actions import HealingAction
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellSaveAction


def build_cure_wounds_2014(wisdom_modifier: int) -> HealingAction:
    return HealingAction(
        id="cure-wounds", name="Cure Wounds", action_cost="action", range_ft=5,
        target_mode="self_or_ally", dice_count=1, dice_size=8,
        healing_bonus=wisdom_modifier + disciple_of_life_bonus(1),
        resource_id="spell-slot-1", resource_cost=1, animation="healing",
    )


def build_healing_word_2014(wisdom_modifier: int) -> HealingAction:
    return HealingAction(
        id="healing-word", name="Healing Word", action_cost="bonus_action", range_ft=60,
        target_mode="self_or_ally", dice_count=1, dice_size=4,
        healing_bonus=wisdom_modifier + disciple_of_life_bonus(1),
        resource_id="spell-slot-1", resource_cost=1, animation="healing",
    )


def build_guiding_bolt_2014(spell_attack_bonus: int) -> SpellAttackAction:
    return build_guiding_bolt(spell_attack_bonus).model_copy(
        update={"source": "D&D Basic Rules 2014: Guiding Bolt"},
        deep=True,
    )


def build_inflict_wounds_2014(spell_attack_bonus: int) -> SpellAttackAction:
    return SpellAttackAction(
        id="inflict-wounds", name="Inflict Wounds", level=1,
        action_cost="action", attack_kind="melee", range_ft=5,
        attack_bonus=spell_attack_bonus, damage_dice_count=3, damage_dice_size=10,
        damage_type="necrotic", animation="inflict-wounds",
        source="D&D Basic Rules 2014: Inflict Wounds",
    )


def build_sacred_flame_2014(save_dc: int, level: int) -> SpellSaveAction:
    return build_sacred_flame(save_dc, level)


def build_defensive_spells_2014() -> list[DefensiveSpellAction]:
    return [
        BLESS.model_copy(update={"source": "D&D Basic Rules 2014: Bless"}, deep=True),
        SHIELD_OF_FAITH.model_copy(
            update={"source": "D&D Basic Rules 2014: Shield of Faith"}, deep=True,
        ),
    ]
