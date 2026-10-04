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
        assert any(item.feature_id == "life-domain" for item in profile.feature_audits)
        assert_canonical_profile_policy(profile)


def test_2024_life_cleric_high_level_blockers_are_explicit() -> None:
    profile = build_seraphine_dawnshield_level20_profile()
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["cleric-combat-spells-7"].automated is True
    assert audits["improved-blessed-strikes"].automated is True
    assert audits["cleric-combat-spells-8"].automated is True
    assert audits["cleric-combat-spells-9"].automated is True
    assert audits["supreme-healing"].automated is True
    assert audits["boon-of-fate"].automated is True
    assert audits["greater-divine-intervention"].automated is True



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



def test_level_fifteen_binds_2024_sunburst() -> None:
    from app.content.audited_cleric import build_seraphine_dawnshield_level

    hero = build_seraphine_dawnshield_level(15)
    sunburst = next(item for item in hero.spell_save_actions if item.id == "sunburst")
    assert sunburst.level == 8
    assert sunburst.save_ability == "constitution"
    assert (sunburst.damage_dice_count, sunburst.damage_dice_size, sunburst.damage_type) == (12, 6, "radiant")
    assert sunburst.success_damage == "half"
    assert sunburst.area is not None
    assert (sunburst.area.shape, sunburst.area.origin, sunburst.area.radius_ft) == ("radius", "point", 60)


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



def test_level_nineteen_binds_boon_of_fate_to_universal_d20_adjustment() -> None:
    from app.content.audited_cleric import build_seraphine_dawnshield_level

    hero = build_seraphine_dawnshield_level(19)
    grants = hero.progression_features.resource_backed_d20_outcome_adjustments
    resources = {item.id: item.max_uses for item in hero.resources}

    assert hero.max_hp == 98
    assert hero.ability_scores.charisma == 20
    assert resources["boon-of-fate"] == 1
    assert len(grants) == 1

    grant = grants[0]
    assert grant.source_id == "boon-of-fate"
    assert grant.resource_id == "boon-of-fate"
    assert (grant.dice_count, grant.dice_size, grant.range_ft) == (2, 4, 60)
    assert grant.test_kinds == ["attack", "saving_throw", "ability_check"]
    assert grant.can_add is True
    assert grant.can_subtract is True

    refills = hero.initiative_resource_refill_grants
    assert len(refills) == 1
    assert refills[0].source_id == "boon-of-fate"
    assert refills[0].resource_id == "boon-of-fate"



def test_level_twenty_binds_greater_divine_intervention_to_2024_wish_fireball() -> None:
    from app.content.audited_cleric import build_seraphine_dawnshield_level

    hero = build_seraphine_dawnshield_level(20)
    actions = {item.id: item for item in hero.saving_throw_actions}
    action = actions["greater-divine-intervention-wish-fireball"]

    assert hero.max_hp == 103
    assert action.name == "Greater Divine Intervention: Wish — Fireball"
    assert action.action_cost == "action"
    assert action.range_ft == 150
    assert action.area is not None
    assert (action.area.shape, action.area.origin, action.area.radius_ft) == ("radius", "point", 20)
    assert action.save_ability == "dexterity"
    assert (action.damage_dice_count, action.damage_dice_size) == (8, 6)
    assert action.damage_type == "fire"
    assert action.success_damage == "half"
    assert action.resource_id == "divine-intervention"
    assert action.resource_cost == 1
