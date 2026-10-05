from __future__ import annotations

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.canonical_hero_policy import canonical_template_id
from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.content.cleric_divine_intervention import (
    build_divine_intervention_damage,
    build_greater_divine_intervention_wish_fireball,
)
from app.content.cleric_life_domain import AID, DISPEL_MAGIC, LESSER_RESTORATION
from app.content.shared_restoration_spells_2024 import greater_restoration_2024
from app.content.shared_survival_spells_2024 import death_ward_2024
from app.content.cleric_runtime_loadout import (
    build_seraphine_healing,
    build_seraphine_initiative_refills,
    build_seraphine_resources,
    build_seraphine_save_spells,
    build_seraphine_save_zones, build_seraphine_timed_self_buffs,
    seraphine_source,
)
from app.content.cleric_runtime_stats import (
    build_seraphine_mace_attack,
    seraphine_saving_throw_bonuses,
    seraphine_skill_bonuses,
)
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.offensive_spell_effects import build_guiding_bolt
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.domain.character_builds import AbilityScores
from app.domain.healing_riders import OutgoingHealingDiceMaximizer
from app.domain.models import CombatantTemplate, VisualLoadout
from app.domain.progression import AbilityScaledDamageRider, ProgressionCombatFeatures, SlotHealingSelfRider
from app.domain.d20_outcome_adjustments import ResourceBackedD20OutcomeAdjustment
from app.domain.progression_primitives import SourceDamageTemporaryHpGrant
from app.domain.traits import CombatTrait
def _modifier(score: int) -> int:
    return (score - 10) // 2


def _features(level: int) -> tuple[str, ...]:
    return canonical_combat_features("cleric", level, "life-domain")


def _build_seraphine(level: int) -> CombatantTemplate:
    if level not in CLERIC_COMBAT_LEVELS:
        raise ValueError(f"Seraphine Cleric level {level} must be between 1 and 20.")
    features = _features(level)
    unsupported = unsupported_hero_engine_features(features)
    if unsupported:
        raise ValueError(
            f"Seraphine Cleric level {level} awaits combat support for: {', '.join(unsupported)}"
        )

    row = CLERIC_COMBAT_LEVELS[level]
    hero = HERO_BY_CLASS["cleric"]
    wisdom_modifier = _modifier(row.wisdom)
    charisma_modifier = _modifier(row.charisma)
    save_dc = 8 + row.proficiency_bonus + wisdom_modifier
    spell_attack_bonus = row.proficiency_bonus + wisdom_modifier

    defenses = [BLESS.model_copy(deep=True), SHIELD_OF_FAITH.model_copy(deep=True)]
    if level >= 3:
        defenses.insert(0, AID.model_copy(deep=True))
    if level >= 7:
        defenses.append(death_ward_2024())

    traits = [CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE]
    if "disciple-of-life" in features:
        traits.append(CombatTrait.LIFE_DOMAIN)

    return CombatantTemplate(
        id=canonical_template_id("cleric", level),
        name=hero.hero_name,
        archetype=hero.class_name,
        level=level,
        kind="character",
        ability_scores=AbilityScores(
            strength=10, dexterity=10, constitution=10, intelligence=14,
            wisdom=row.wisdom, charisma=row.charisma,
        ),
        armor_class=row.armor_class,
        max_hp=row.max_hp,
        speed_ft=30,
        initiative_bonus=0,
        weapon_attack=build_seraphine_mace_attack(row.proficiency_bonus),
        saving_throw_actions=(
            [build_divine_intervention_damage(save_dc)]
            + ([build_greater_divine_intervention_wish_fireball(save_dc)] if level >= 20 else [])
            if level >= 10 else []
        ),
        spell_save_actions=build_seraphine_save_spells(level, save_dc, wisdom_modifier, features),
        spell_attack_actions=[build_guiding_bolt(spell_attack_bonus)],
        defensive_spell_actions=defenses,
        healing_actions=build_seraphine_healing(level, wisdom_modifier, features),
        condition_removal_actions=[
            *([LESSER_RESTORATION.model_copy(deep=True)] if level >= 3 else []),
            *([greater_restoration_2024()] if level >= 9 else []),
        ],
        persistent_save_zone_actions=build_seraphine_save_zones(level, save_dc),
        effect_removal_actions=[DISPEL_MAGIC.model_copy(deep=True)] if level >= 5 else [],
        support_action_modes=["turn-undead", "divine-spark", *(["preserve-life"] if level >= 3 else [])] if level >= 2 else [],
        progression_features=ProgressionCombatFeatures(
            turning_failure_damage=(
                AbilityScaledDamageRider(
                    source_id="sear-undead", ability="wisdom",
                    dice_size=8, damage_type="radiant",
                )
                if level >= 5 else None
            ),
            slot_healing_other_self_rider=(
                SlotHealingSelfRider(
                    source_id="blessed-healer", flat_bonus=2, per_slot_level=1,
                )
                if level >= 6 else None
            ),
            outgoing_healing_dice_maximizer=(
                OutgoingHealingDiceMaximizer(
                    source_id="supreme-healing",
                    source_name="Supreme Healing",
                )
                if "supreme-healing" in features else None
            ),
            resource_backed_d20_outcome_adjustments=(
                [
                    ResourceBackedD20OutcomeAdjustment(
                        source_id="boon-of-fate",
                        source_name="Boon of Fate",
                        resource_id="boon-of-fate",
                        dice_count=2,
                        dice_size=4,
                        range_ft=60,
                        test_kinds=["attack", "saving_throw", "ability_check"],
                        can_add=True,
                        can_subtract=True,
                    )
                ]
                if "boon-of-fate" in features else []
            ),
            source_damage_temporary_hp=(
                SourceDamageTemporaryHpGrant(
                    source_id="improved-blessed-strikes",
                    source_name="Improved Blessed Strikes",
                    trigger_action_ids=["sacred-flame"],
                    ability="wisdom",
                    ability_multiplier=2,
                )
                if "improved-blessed-strikes" in features else None
            ),
        ),
        saving_throw_bonuses=seraphine_saving_throw_bonuses(
            row.proficiency_bonus, wisdom_modifier, charisma_modifier,
        ),
        skill_bonuses=seraphine_skill_bonuses(
            row.proficiency_bonus, wisdom_modifier, charisma_modifier,
        ),
        combat_traits=traits,
        visual=VisualLoadout(armor="chain-shirt", main_hand="mace", off_hand="shield", body_style="humanoid"),
        resources=build_seraphine_resources(level),
        initiative_resource_refill_grants=build_seraphine_initiative_refills(level),
        timed_self_buff_actions=build_seraphine_timed_self_buffs(level, save_dc),
        source=seraphine_source(level),
    )


def build_seraphine_dawnshield_level(level: int) -> CombatantTemplate:
    """Compile Seraphine from Cleric base + Life Domain overlay; missing combat content fails closed."""
    return _build_seraphine(level)


def build_seraphine_dawnshield() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(1)


def build_seraphine_dawnshield_level_two() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(2)


def build_seraphine_dawnshield_level_three() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(3)


def build_seraphine_dawnshield_level_four() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(4)


def build_seraphine_dawnshield_level_five() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(5)


def build_seraphine_dawnshield_level_six() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(6)


def build_seraphine_dawnshield_level_seven() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(7)


def build_seraphine_dawnshield_level_eight() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(8)
