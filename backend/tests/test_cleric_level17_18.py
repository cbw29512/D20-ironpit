from app.combat.cleric_divine_spark import resolve_divine_spark
from app.combat.dice import FixedDiceProvider
from app.combat.healing import resolve_healing
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_high_profile import (
    build_seraphine_dawnshield_level17_profile,
    build_seraphine_dawnshield_level18_profile,
)
from app.content.audited_fighter import build_karnok_stoneward
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template.model_copy(deep=True)),
    )


def _resources(template) -> dict[str, int]:
    return {item.id: item.max_uses for item in template.resources}


def _assert_ready(level: int, profile) -> None:
    hero = build_seraphine_dawnshield_level(level)
    combat = build_pregen_combat_profiles()[hero.id]
    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_seventeen_certifies_ninth_level_upcasts_and_supreme_healing() -> None:
    hero = build_seraphine_dawnshield_level(17)
    profile = build_seraphine_dawnshield_level17_profile()
    package = canonical_spell_package("cleric", 17)

    assert (hero.max_hp, hero.ability_scores.wisdom, hero.ability_scores.charisma) == (88, 20, 19)
    assert _resources(hero) == {
        "spell-slot-1": 4, "spell-slot-2": 3, "spell-slot-3": 3, "spell-slot-4": 3,
        "spell-slot-5": 2, "spell-slot-6": 1, "spell-slot-7": 1, "spell-slot-8": 1,
        "spell-slot-9": 1, "channel-divinity": 3, "divine-intervention": 1,
        "adrenaline-rush": 6, "relentless-endurance": 1,
    }
    damage = next(item for item in hero.spell_save_actions if item.id == "inflict-wounds-l9")
    healing = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds-l9")
    assert (damage.level, damage.damage_dice_count, damage.damage_dice_size, damage.dc) == (9, 10, 10, 19)
    assert (healing.dice_count, healing.dice_size, healing.healing_bonus) == (9, 8, 16)
    assert len(package.spells) == 19 and package.spells[-1].id == "astral-projection"

    maximizer = hero.progression_features.healing_dice_maximizer
    assert maximizer is not None and maximizer.source_id == "supreme-healing"
    assert {item.id for item in hero.healing_actions} <= set(maximizer.healing_source_ids)
    assert "divine-spark" in maximizer.healing_source_ids
    assert hero.progression_features.feature_dice_counts["divine-spark"] == 3

    cleric = _member(hero, "cleric", "heroes", 0)
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 5)
    ally.state.current_hp = 1
    cure = next(item for item in hero.healing_actions if item.id == "cure-wounds")
    event = resolve_healing(1, 1, cleric, ally, cure, FixedDiceProvider([1, 1]), "1:cleric")
    assert event.healing_roll.rolls == [8, 8]
    assert event.healing_roll.total == 24

    spark_cleric = _member(hero, "spark-cleric", "heroes", 0)
    spark_ally = _member(build_karnok_stoneward(), "spark-ally", "heroes", 5)
    spark_ally.state.current_hp = 1
    enemy = _member(build_karnok_stoneward(), "enemy", "monsters", 10)
    setup = EncounterSetup(
        heroes=[spark_cleric, spark_ally], monsters=[enemy],
        hero_total_levels=18, monster_total_cr="1",
    )
    spark = resolve_divine_spark(
        2, 1, spark_cleric, spark_ally, setup, FixedDiceProvider([1]),
        healing=True, save_dc=19, resource_remaining=2,
    )
    assert spark.healing_roll.rolls == [8, 8, 8]
    assert spark.healing_roll.total == 29
    _assert_ready(17, profile)


def test_level_eighteen_scales_channel_divinity_and_divine_spark_to_four_dice() -> None:
    hero = build_seraphine_dawnshield_level(18)
    profile = build_seraphine_dawnshield_level18_profile()
    package = canonical_spell_package("cleric", 18)
    resources = _resources(hero)

    assert (hero.max_hp, hero.ability_scores.wisdom, hero.ability_scores.charisma) == (93, 20, 19)
    assert resources["spell-slot-5"] == 3 and resources["channel-divinity"] == 4
    assert hero.progression_features.feature_dice_counts["divine-spark"] == 4
    assert len(package.spells) == 20 and package.spells[-1].id == "word-of-recall"

    cleric = _member(hero, "cleric", "heroes", 0)
    target = _member(build_karnok_stoneward(), "target", "monsters", 10)
    setup = EncounterSetup(heroes=[cleric], monsters=[target], hero_total_levels=18, monster_total_cr="1")
    event = resolve_divine_spark(
        1, 1, cleric, target, setup, FixedDiceProvider([1, 2, 3, 4, 1]),
        healing=False, save_dc=19, resource_remaining=3,
    )
    assert event.damage_roll.notation == "4d8+5"
    assert event.damage_roll.rolls == [1, 2, 3, 4]
    _assert_ready(18, profile)


def test_registry_exposes_seventeen_and_eighteen_but_not_nineteen() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 17, "canonical")][1] == "seraphine-dawnshield-l17"
    assert registry[("cleric", 18, "canonical")][1] == "seraphine-dawnshield-l18"
    assert ("cleric", 19, "canonical") not in registry
