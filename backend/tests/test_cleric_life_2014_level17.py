from app.combat.dice import FixedDiceProvider
from app.combat.healing_policy import healing_dice_maximized
from app.combat.healing_resolution_support import resolve_healing_amount
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant


def _member(template, combatant_id: str, side: str = "heroes") -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=0,
        state=build_combatant_state(template),
    )


def test_level_seventeen_advances_level_sixteen_without_rebuilding_seraphine() -> None:
    level_sixteen = build_seraphine_dawnshield_2014_profile(16)
    level_seventeen = build_seraphine_dawnshield_2014_profile(17)

    assert level_seventeen.character_name == level_sixteen.character_name == "Seraphine Dawnshield"
    assert level_seventeen.species_id == level_sixteen.species_id == "hill-dwarf"
    assert level_seventeen.background_id == level_sixteen.background_id == "acolyte"
    assert level_seventeen.subclass_id == level_sixteen.subclass_id == "life-domain"
    assert level_seventeen.class_equipment == level_sixteen.class_equipment
    assert level_seventeen.advancement_increases == level_sixteen.advancement_increases
    assert level_seventeen.final_ability_scores == level_sixteen.final_ability_scores
    assert level_seventeen.feature_audits[: len(level_sixteen.feature_audits)] == level_sixteen.feature_audits
    assert [item.feature_id for item in level_seventeen.feature_audits[-2:]] == [
        "destroy-undead-4",
        "supreme-healing",
    ]


def test_level_seventeen_runtime_binds_cr_four_and_supreme_healing() -> None:
    hero = build_seraphine_dawnshield_2014(17)
    profile = build_seraphine_dawnshield_2014_profile(17)
    combat = build_seraphine_2014_combat_profile(17)

    assert hero.max_hp == 189
    assert hero.armor_class == 16
    assert hero.ability_scores is not None
    assert hero.ability_scores.constitution == 20
    assert hero.ability_scores.wisdom == 20
    assert hero.progression_features.turning_failure_destroy_max_cr == "4"

    maximizer = hero.progression_features.outgoing_healing_dice_maximizer
    assert maximizer is not None
    assert (maximizer.source_id, maximizer.source_name) == (
        "supreme-healing",
        "Supreme Healing",
    )

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
        "channel-divinity": 2,
        "divine-intervention": 1,
    }

    sacred_flame = next(item for item in hero.spell_save_actions if item.id == "sacred-flame")
    assert sacred_flame.damage_dice_count == 4
    assert sacred_flame.dc == 19

    upcast = next(item for item in hero.spell_attack_actions if item.id == "inflict-wounds-l9")
    assert upcast.attack_bonus == 11
    assert (upcast.damage_dice_count, upcast.damage_dice_size, upcast.damage_type) == (
        11, 10, "necrotic",
    )

    intervention = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert intervention.percentile_success_max == 17

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_seventeen_supreme_healing_uses_generic_outgoing_maximizer() -> None:
    healer = _member(build_seraphine_dawnshield_2014(17), "cleric")
    target = _member(build_seraphine_dawnshield_2014(16), "ally")
    target.state.current_hp = 100

    action = next(
        item for item in healer.state.template.healing_actions
        if item.id == "healing-word"
    )

    assert healing_dice_maximized(healer, target) is True
    rolls, total, healed, notation, modifier = resolve_healing_amount(
        healer,
        target,
        action,
        FixedDiceProvider([1]),
    )

    assert rolls == [action.dice_size]
    assert total == action.dice_size + action.healing_bonus
    assert healed == total
    assert notation == f"{action.dice_count}d{action.dice_size}+{action.healing_bonus}"
    assert modifier == action.healing_bonus


def test_level_seventeen_spell_package_expands_prepared_count_legally() -> None:
    package = build_cleric_2014_spell_package(17, 5)

    assert len(package.spells) == 22
    assert package.spells[-1].id == "commune"
    assert package.casting_ability == "wisdom"
