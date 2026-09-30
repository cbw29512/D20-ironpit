from __future__ import annotations

from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_2024_druid_level_nine_progression_prioritizes_damage_and_healing() -> None:
    hero = build_thalen_greenbough_level(9)
    profile = build_thalen_greenbough_profile(9)
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("druid", 9, "2024", 5)

    assert hero.level == 9
    assert hero.max_hp == 48
    assert hero.ability_scores.wisdom == 20
    assert hero.ability_scores.charisma == 16
    assert hero.saving_throw_bonuses["wisdom"] == 9
    assert hero.saving_throw_bonuses["intelligence"] == 5
    assert hero.skill_bonuses["nature"] == 10
    assert hero.skill_bonuses["survival"] == 9
    assert hero.skill_bonuses["insight"] == 9
    assert hero.skill_bonuses["religion"] == 5
    assert hero.skill_bonuses["perception"] == 9

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 1,
        "wild-shape": 3,
        "wild-resurgence-slot-restore": 1,
        "natural-recovery-free-cast": 1,
    }

    assert package is not None
    assert len(package.spells) == 14
    assert [spell.id for spell in package.spells][-2:] == [
        "cone-of-cold",
        "mass-cure-wounds",
    ]

    cone = next(item for item in hero.spell_save_actions if item.id == "cone-of-cold")
    assert cone.level == 5
    assert cone.save_ability == "constitution"
    assert cone.damage_dice_count == 8
    assert cone.damage_dice_size == 8
    assert cone.damage_type == "cold"
    assert cone.success_damage == "half"
    assert cone.upcast_dice_per_level == 1
    assert cone.area is not None
    assert cone.area.shape == "cone"
    assert cone.area.origin == "self"
    assert cone.area.length_ft == 60

    mass = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds")
    assert mass.action_cost == "action"
    assert mass.range_ft == 60
    assert mass.area_radius_ft == 30
    assert mass.max_targets == 6
    assert mass.dice_count == 5
    assert mass.dice_size == 8
    assert mass.healing_bonus == 5
    assert mass.resource_id == "spell-slot-5"

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["druid-combat-spells-5"].automated is True
    assert audits["circle-spells-5-wall-of-stone"].combat_relevant is True
    assert audits["circle-spells-5-wall-of-stone"].automated is True

    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)
