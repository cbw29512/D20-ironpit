from app.content.hero_combat_feature_registry import (
    compile_progression_feature_fields,
    unsupported_hero_engine_features,
)


def test_shared_feature_registry_compiles_reusable_fighter_and_barbarian_flags() -> None:
    fighter = compile_progression_feature_fields(
        ("improved-critical", "remarkable-athlete", "great-weapon-fighting", "indomitable", "heroic-warrior", "studied-attacks"), 13,
    )
    assert fighter == {
        "critical_hit_minimum": 19,
        "initiative_advantage": True,
        "athletics_advantage": True,
        "critical_move_fraction": 0.5,
        "great_weapon_fighting": True,
        "indomitable_bonus": 13,
        "heroic_warrior": True,
        "studied_attacks": True,
    }

    barbarian = compile_progression_feature_fields(
        ("danger-sense", "reckless-attack", "frenzy", "fast-movement", "mindless-rage", "feral-instinct"), 7,
    )
    assert barbarian == {
        "danger_sense": True,
        "reckless_attack": True,
        "frenzy": True,
        "fast_movement_bonus_ft": 10,
        "mindless_rage": True,
        "initiative_advantage": True,
    }


def test_shared_feature_registry_fails_closed_for_unimplemented_combat_mechanics() -> None:
    assert unsupported_hero_engine_features(("rage", "frenzy")) == ()
    assert unsupported_hero_engine_features(("heroic-warrior", "studied-attacks")) == ()
    assert unsupported_hero_engine_features(("rage", "instinctive-pounce", "brutal-strike")) == (
        "instinctive-pounce", "brutal-strike",
    )
    assert unsupported_hero_engine_features(("studied-attacks", "superior-critical")) == ("superior-critical",)
