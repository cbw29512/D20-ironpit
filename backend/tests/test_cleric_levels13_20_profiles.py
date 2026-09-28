from app.content.audited_cleric_life_high_profile import (
    build_seraphine_dawnshield_level13_profile,
    build_seraphine_dawnshield_level14_profile,
    build_seraphine_dawnshield_level15_profile,
    build_seraphine_dawnshield_level16_profile,
    build_seraphine_dawnshield_level17_profile,
    build_seraphine_dawnshield_level18_profile,
    build_seraphine_dawnshield_level19_profile,
    build_seraphine_dawnshield_level20_profile,
)
from app.content.canonical_hero_policy import assert_canonical_profile_policy


def test_2024_life_cleric_profiles_stage_cleanly_through_level_twenty() -> None:
    builders = (
        build_seraphine_dawnshield_level13_profile,
        build_seraphine_dawnshield_level14_profile,
        build_seraphine_dawnshield_level15_profile,
        build_seraphine_dawnshield_level16_profile,
        build_seraphine_dawnshield_level17_profile,
        build_seraphine_dawnshield_level18_profile,
        build_seraphine_dawnshield_level19_profile,
        build_seraphine_dawnshield_level20_profile,
    )

    profiles = [builder() for builder in builders]
    assert [profile.level for profile in profiles] == list(range(13, 21))
    assert [(p.final_ability_scores.wisdom, p.final_ability_scores.charisma) for p in profiles] == [
        (20, 17), (20, 17), (20, 17), (20, 19),
        (20, 19), (20, 19), (20, 20), (20, 20),
    ]

    for profile in profiles:
        assert profile.character_name == "Seraphine Dawnshield"
        assert profile.ruleset == "2024"
        assert profile.subclass_id == "life-domain"
        assert_canonical_profile_policy(profile)


def test_2024_life_cleric_high_level_blockers_are_explicit() -> None:
    profile = build_seraphine_dawnshield_level20_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["cleric-combat-spells-7"].automated is True
    assert audits["improved-blessed-strikes"].automated is True
    assert audits["cleric-combat-spells-8"].automated is True
    assert audits["cleric-combat-spells-9"].automated is True
    assert audits["supreme-healing"].automated is True
    assert audits["boon-of-fate"].automated is False
    assert audits["greater-divine-intervention"].automated is False



def test_level_thirteen_reuses_existing_seventh_level_spell_primitives() -> None:
    from app.content.audited_cleric import build_seraphine_dawnshield_level

    hero = build_seraphine_dawnshield_level(13)
    resources = {item.id: item.max_uses for item in hero.resources}

    assert hero.max_hp == 68
    assert resources["spell-slot-7"] == 1
    assert resources["channel-divinity"] == 3

    damage = next(item for item in hero.spell_save_actions if item.id == "inflict-wounds-l7")
    healing = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds-l7")

    assert (damage.level, damage.damage_dice_count, damage.damage_dice_size) == (7, 8, 10)
    assert (healing.dice_count, healing.dice_size) == (7, 8)
    assert healing.resource_id == "spell-slot-7"



def test_level_fourteen_binds_improved_blessed_strikes_to_universal_trigger() -> None:
    from app.content.audited_cleric import build_seraphine_dawnshield_level

    hero = build_seraphine_dawnshield_level(14)
    grant = hero.progression_features.source_damage_temporary_hp

    assert hero.max_hp == 73
    assert hero.ability_scores.wisdom == 20
    assert grant is not None
    assert grant.source_id == "improved-blessed-strikes"
    assert grant.trigger_action_ids == ["sacred-flame"]
    assert grant.ability == "wisdom"
    assert grant.ability_multiplier == 2
