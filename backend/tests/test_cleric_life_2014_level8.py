from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats


# Exact-head verification guard: level 8 remains one persistent Seraphine progression.
def test_level_eight_advances_level_seven_and_applies_existing_asi() -> None:
    level_seven = build_seraphine_dawnshield_2014_profile(7)
    level_eight = build_seraphine_dawnshield_2014_profile(8)

    assert level_eight.character_name == level_seven.character_name == "Seraphine Dawnshield"
    assert level_eight.species_id == level_seven.species_id == "hill-dwarf"
    assert level_eight.background_id == level_seven.background_id == "acolyte"
    assert level_eight.subclass_id == level_seven.subclass_id == "life-domain"
    assert level_eight.class_equipment == level_seven.class_equipment
    assert level_eight.advancement_increases[:-1] == level_seven.advancement_increases
    assert (level_eight.advancement_increases[-1].ability, level_eight.advancement_increases[-1].amount) == (
        "wisdom", 2,
    )
    assert level_seven.final_ability_scores.wisdom == 18
    assert level_eight.final_ability_scores.wisdom == 20


def test_level_eight_runtime_adds_destroy_threshold_and_divine_strike() -> None:
    hero = build_seraphine_dawnshield_2014(8)
    profile = build_seraphine_dawnshield_2014_profile(8)
    combat = build_seraphine_2014_combat_profile(8)

    assert hero.max_hp == 75
    assert hero.armor_class == 16
    assert hero.ability_scores is not None and hero.ability_scores.wisdom == 20
    assert hero.progression_features.turning_failure_destroy_max_cr == "1"
    rider = hero.progression_features.once_per_turn_weapon_hit_damage_rider
    assert rider is not None
    assert (
        rider.source_id,
        rider.source_name,
        rider.dice_count,
        rider.dice_size,
        rider.damage_type,
    ) == ("divine-strike", "Divine Strike", 1, 8, "radiant")
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 2,
        "channel-divinity": 2,
    }

    sacred_flame = next(item for item in hero.spell_save_actions if item.id == "sacred-flame")
    guiding_bolt = next(item for item in hero.spell_attack_actions if item.id == "guiding-bolt")
    assert sacred_flame.dc == 16
    assert guiding_bolt.attack_bonus == 8

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_eight_divine_strike_uses_generic_once_per_turn_weapon_hit_rider() -> None:
    state = build_combatant_state(build_seraphine_dawnshield_2014(8))
    attack = state.template.weapon_attack

    first, first_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([4, 6]), False, "normal", "1:seraphine",
    )
    assert [part.source for part in first_components] == ["Warhammer", "Divine Strike"]
    assert first_components[1].damage_type.value == "radiant"
    assert first.total == 11

    second, second_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([5]), False, "normal", "1:seraphine",
    )
    assert [part.source for part in second_components] == ["Warhammer"]
    assert second.total == 6

    third, third_components = resolve_weapon_damage(
        state, attack, FixedDiceProvider([3, 7]), False, "normal", "2:seraphine",
    )
    assert [part.source for part in third_components] == ["Warhammer", "Divine Strike"]
    assert third.total == 11
