from app.combat.condition_immunity import condition_is_immune
from app.combat.defensive_modifier_rules import attacks_against_disadvantage_sources, effect_is_immune
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014


def _resource_map(level: int) -> dict[str, int]:
    runtime = build_aurelia_brightshield_2014(level)
    return {item.id: item.max_uses for item in runtime.resources}


def test_aurelia_prepared_progression_reaches_level_twenty_without_identity_drift() -> None:
    first = build_aurelia_brightshield_2014_profile(1)
    prior = first
    for level in range(2, 21):
        current = build_aurelia_brightshield_2014_profile(level)
        runtime = build_aurelia_brightshield_2014(level)
        fingerprint = build_aurelia_brightshield_2014_combat_profile(level)

        assert current.character_name == first.character_name == "Aurelia Brightshield"
        assert current.species_id == first.species_id == "human"
        assert current.background_id == first.background_id == "noble"
        assert current.class_equipment == first.class_equipment
        assert runtime.id == current.template_id == fingerprint.template_id
        assert runtime.level == current.level == fingerprint.level == level
        assert runtime.ruleset == current.ruleset == "2014"
        assert len(current.advancement_increases) >= len(prior.advancement_increases)
        prior = current

    level_16 = build_aurelia_brightshield_2014_profile(16)
    level_19 = build_aurelia_brightshield_2014_profile(19)
    assert level_16.final_ability_scores.strength == 20
    assert level_16.final_ability_scores.charisma == 19
    assert level_19.final_ability_scores.charisma == 20
    assert level_19.final_ability_scores.constitution == 15


def test_aurelia_prepared_high_level_slots_and_resources_match_2014_progression() -> None:
    expected_slots = {
        13: (4, 3, 3, 1),
        14: (4, 3, 3, 1),
        15: (4, 3, 3, 2),
        16: (4, 3, 3, 2),
        17: (4, 3, 3, 3, 1),
        18: (4, 3, 3, 3, 1),
        19: (4, 3, 3, 3, 2),
        20: (4, 3, 3, 3, 2),
    }
    for level, slots in expected_slots.items():
        resources = _resource_map(level)
        assert resources["lay-on-hands"] == 5 * level
        assert resources["channel-divinity"] == 1
        assert tuple(resources[f"spell-slot-{index}"] for index in range(1, len(slots) + 1)) == slots
        if level >= 14:
            assert resources["cleansing-touch"] == (3 if level < 16 else 4 if level < 19 else 5)
        else:
            assert "cleansing-touch" not in resources
        if level == 20:
            assert resources["holy-nimbus"] == 1
        else:
            assert "holy-nimbus" not in resources


def test_high_level_preparation_keeps_unfinished_features_explicitly_uncertified() -> None:
    expected_blocked = {
        20: "holy-nimbus",
    }
    for level, feature_id in expected_blocked.items():
        profile = build_aurelia_brightshield_2014_profile(level)
        audit = next(item for item in profile.feature_audits if item.feature_id == feature_id)
        assert audit.combat_relevant is True
        assert audit.automated is False

    certified = next(
        item for item in CERTIFIED_HERO_PROGRESSIONS
        if item.class_id == "paladin" and item.template_builder is build_aurelia_brightshield_2014
    )
    assert certified.max_level == 12


def test_cleansing_touch_is_no_check_generic_effect_removal() -> None:
    runtime = build_aurelia_brightshield_2014(14)
    action = next(item for item in runtime.effect_removal_actions if item.id == "cleansing-touch")
    assert action.action_cost == "action"
    assert action.range_ft == 5
    assert action.target_mode == "self_or_ally"
    assert action.resource_id == "cleansing-touch"
    assert action.resource_cost == 1
    assert action.expends_spell_slot is False
    assert action.auto_remove_max_level == 9

    audit = next(
        item for item in build_aurelia_brightshield_2014_profile(14).feature_audits
        if item.feature_id == "cleansing-touch"
    )
    assert audit.automated is True


def test_level_eighteen_aura_radius_is_prepared() -> None:
    runtime = build_aurelia_brightshield_2014(18)
    assert runtime.progression_features.paladin_aura_radius_2014_ft == 30
    audit = next(
        item for item in build_aurelia_brightshield_2014_profile(18).feature_audits
        if item.feature_id == "aura-improvements"
    )
    assert audit.automated is True


def test_purity_of_spirit_typed_defenses_use_opening_modifier_engine() -> None:
    state = build_combatant_state(build_aurelia_brightshield_2014(15))
    fiend = build_commoner().model_copy(update={"ruleset": "2014", "creature_type": "fiend"})
    humanoid = build_commoner().model_copy(update={"ruleset": "2014", "creature_type": "humanoid"})

    purity = [item for item in state.active_modifiers if item.source_effect_id == "purity-of-spirit"]
    assert len(purity) == 4
    assert {item.source_name for item in purity} == {"Purity of Spirit"}
    assert attacks_against_disadvantage_sources(state, fiend) == 1
    assert attacks_against_disadvantage_sources(state, humanoid) == 0
    assert condition_is_immune(state, "charmed", fiend) is True
    assert condition_is_immune(state, "frightened", fiend) is True
    assert condition_is_immune(state, "charmed", humanoid) is False
    assert effect_is_immune(state, "possession", fiend) is True
    assert effect_is_immune(state, "possession", humanoid) is False

    audit = next(
        item for item in build_aurelia_brightshield_2014_profile(15).feature_audits
        if item.feature_id == "purity-of-spirit"
    )
    assert audit.automated is True
    assert "possession-effect immunity" in (audit.notes or "")


def test_level_seventeen_flame_strike_uses_one_save_with_two_typed_components() -> None:
    runtime = build_aurelia_brightshield_2014(17)
    assert len(runtime.spell_save_actions) == 1
    flame_strike = runtime.spell_save_actions[0]
    assert flame_strike.id == "flame-strike"
    assert flame_strike.level == 5
    assert flame_strike.save_ability == "dexterity"
    assert flame_strike.dc == 18
    assert flame_strike.success_damage == "half"
    assert [(item.dice_count, item.dice_size, item.damage_type) for item in flame_strike.damage_components] == [
        (4, 6, "fire"),
        (4, 6, "radiant"),
    ]
    audit = next(
        item for item in build_aurelia_brightshield_2014_profile(17).feature_audits
        if item.feature_id == "devotion-oath-spells-5"
    )
    assert audit.automated is True
