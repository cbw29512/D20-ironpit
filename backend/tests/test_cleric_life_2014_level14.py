from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_fourteen_advances_level_thirteen_without_rebuilding_seraphine() -> None:
    level_thirteen = build_seraphine_dawnshield_2014_profile(13)
    level_fourteen = build_seraphine_dawnshield_2014_profile(14)

    assert level_fourteen.character_name == level_thirteen.character_name == "Seraphine Dawnshield"
    assert level_fourteen.species_id == level_thirteen.species_id == "hill-dwarf"
    assert level_fourteen.background_id == level_thirteen.background_id == "acolyte"
    assert level_fourteen.subclass_id == level_thirteen.subclass_id == "life-domain"
    assert level_fourteen.class_equipment == level_thirteen.class_equipment
    assert level_fourteen.advancement_increases == level_thirteen.advancement_increases
    assert level_fourteen.final_ability_scores == level_thirteen.final_ability_scores
    assert level_fourteen.feature_audits[: len(level_thirteen.feature_audits)] == level_thirteen.feature_audits
    assert [item.feature_id for item in level_fourteen.feature_audits[-2:]] == [
        "destroy-undead-3",
        "divine-strike-2d8",
    ]


def test_level_fourteen_runtime_scales_existing_turning_and_divine_strike_primitives() -> None:
    hero = build_seraphine_dawnshield_2014(14)
    profile = build_seraphine_dawnshield_2014_profile(14)
    combat = build_seraphine_2014_combat_profile(14)

    assert hero.max_hp == 143
    assert hero.armor_class == 16
    assert hero.ability_scores is not None
    assert hero.ability_scores.constitution == 18
    assert hero.ability_scores.wisdom == 20
    assert hero.progression_features.turning_failure_destroy_max_cr == "3"

    rider = hero.progression_features.once_per_turn_weapon_hit_damage_rider
    assert rider is not None
    assert (
        rider.source_id,
        rider.source_name,
        rider.dice_count,
        rider.dice_size,
        rider.damage_type,
    ) == ("divine-strike", "Divine Strike", 2, 8, "radiant")

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "channel-divinity": 2,
        "divine-intervention": 1,
    }

    intervention = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert intervention.percentile_success_max == 14

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_fourteen_divine_strike_2d8_reuses_generic_once_per_turn_hit_rider() -> None:
    state = build_combatant_state(build_seraphine_dawnshield_2014(14))
    attack = state.template.weapon_attack

    first, first_components = resolve_weapon_damage(
        state,
        attack,
        FixedDiceProvider([4, 6, 7]),
        False,
        "normal",
        "1:seraphine",
    )
    assert [part.source for part in first_components] == ["Warhammer", "Divine Strike"]
    assert first_components[1].rolls == [6, 7]
    assert first_components[1].damage_type.value == "radiant"
    assert first.total == 18

    second, second_components = resolve_weapon_damage(
        state,
        attack,
        FixedDiceProvider([5]),
        False,
        "normal",
        "1:seraphine",
    )
    assert [part.source for part in second_components] == ["Warhammer"]
    assert second.total == 6


def test_level_fourteen_spell_package_expands_prepared_count_legally() -> None:
    package = build_cleric_2014_spell_package(14, 5)

    assert len(package.spells) == 19
    assert package.spells[-1].id == "locate-creature"
    assert package.casting_ability == "wisdom"
