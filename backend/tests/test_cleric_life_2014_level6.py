from app.combat.healing_riders import apply_slot_healing_self_rider
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant


def _member(template, combatant_id: str) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side="heroes",
        position_ft=0,
        state=build_combatant_state(template),
    )


def test_level_six_advances_level_five_without_rebuilding_seraphine() -> None:
    level_five = build_seraphine_dawnshield_2014_profile(5)
    level_six = build_seraphine_dawnshield_2014_profile(6)

    assert level_six.character_name == level_five.character_name == "Seraphine Dawnshield"
    assert level_six.species_id == level_five.species_id == "hill-dwarf"
    assert level_six.background_id == level_five.background_id == "acolyte"
    assert level_six.subclass_id == level_five.subclass_id == "life-domain"
    assert level_six.class_equipment == level_five.class_equipment
    assert level_six.advancement_increases == level_five.advancement_increases
    assert level_six.final_ability_scores == level_five.final_ability_scores
    assert level_six.feature_audits[: len(level_five.feature_audits)] == level_five.feature_audits
    assert [item.feature_id for item in level_six.feature_audits[-2:]] == [
        "channel-divinity-2",
        "blessed-healer",
    ]


def test_level_six_runtime_adds_only_channel_divinity_and_blessed_healer_delta() -> None:
    hero = build_seraphine_dawnshield_2014(6)
    profile = build_seraphine_dawnshield_2014_profile(6)
    combat = build_seraphine_2014_combat_profile(6)

    assert hero.max_hp == 57
    assert hero.armor_class == 16
    assert hero.ability_scores is not None and hero.ability_scores.wisdom == 18
    assert hero.progression_features.turning_failure_destroy_max_cr == "1/2"
    rider = hero.progression_features.slot_healing_other_self_rider
    assert rider is not None
    assert (rider.source_id, rider.flat_bonus, rider.per_slot_level) == (
        "blessed-healer", 2, 1,
    )
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "channel-divinity": 2,
    }

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_six_blessed_healer_reuses_universal_slotted_healing_self_rider() -> None:
    cleric = _member(build_seraphine_dawnshield_2014(6), "cleric")
    ally = _member(build_seraphine_dawnshield_2014(5), "ally")
    cleric.state.current_hp = 20
    ally.state.current_hp = 1

    action = next(
        item for item in cleric.state.template.healing_actions
        if item.id == "healing-word"
    )
    before = cleric.state.current_hp
    event = apply_slot_healing_self_rider(
        1, 1, cleric, True, action,
    )

    assert event is not None
    assert event.feature_id == "blessed-healer"
    assert cleric.state.current_hp == before + 3


def test_level_six_spell_preparation_expands_on_same_character() -> None:
    package = build_cleric_2014_spell_package(6, 4)

    assert [spell.id for spell in package.spells] == [
        "healing-word",
        "guiding-bolt",
        "shield-of-faith",
        "inflict-wounds",
        "sanctuary",
        "aid",
        "detect-magic",
        "augury",
        "prayer-of-healing",
        "warding-bond",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "bless",
        "cure-wounds",
        "lesser-restoration",
        "spiritual-weapon",
        "beacon-of-hope",
        "revivify",
    ]
