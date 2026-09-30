from __future__ import annotations

from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_2024_druid_level_fourteen_adds_sanctuary_without_spell_package_drift() -> None:
    hero = build_thalen_greenbough_level(14)
    profile = build_thalen_greenbough_profile(14)
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("druid", 14, "2024", 7)

    assert hero.level == 14
    assert hero.max_hp == 73
    assert hero.ability_scores.wisdom == 20
    assert hero.ability_scores.charisma == 18
    assert hero.saving_throw_bonuses["wisdom"] == 10
    assert hero.saving_throw_bonuses["intelligence"] == 6
    assert hero.skill_bonuses["nature"] == 11
    assert hero.skill_bonuses["survival"] == 10
    assert hero.skill_bonuses["insight"] == 10
    assert hero.skill_bonuses["religion"] == 6
    assert hero.skill_bonuses["perception"] == 10

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "wild-shape": 3,
        "wild-resurgence-slot-restore": 1,
        "natural-recovery-free-cast": 1,
    }

    assert package is not None
    assert len(package.spells) == 17
    assert package.spells[-1].id == "fire-storm"

    lands_aid = next(item for item in hero.saving_throw_actions if item.id == "lands-aid")
    assert lands_aid.damage_dice_count == 4
    assert lands_aid.damage_dice_size == 6
    assert lands_aid.area_healing_rider is not None
    assert lands_aid.area_healing_rider.dice_count == 4
    assert lands_aid.area_healing_rider.dice_size == 6

    assert len(hero.persistent_beneficial_zone_actions) == 1
    sanctuary = hero.persistent_beneficial_zone_actions[0]
    assert sanctuary.id == "natures-sanctuary"
    assert sanctuary.resource_id == "wild-shape"
    assert sanctuary.resource_cost == 1
    assert sanctuary.cast_range_ft == 120
    assert sanctuary.duration_rounds == 10
    assert sanctuary.shape == "cube"
    assert sanctuary.length_ft == 15
    assert sanctuary.move_action_cost == "bonus_action"
    assert sanctuary.move_distance_ft == 60
    assert sanctuary.move_range_ft == 120
    assert sanctuary.armor_class_bonus == 2
    assert sanctuary.saving_throw_bonus == 2
    assert sanctuary.saving_throw_abilities == ["dexterity"]
    assert sanctuary.ally_damage_resistances == ["fire"]
    assert sanctuary.end_if_source_incapacitated is True
    assert sanctuary.end_if_source_dead is True

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["natures-sanctuary"].combat_relevant is True
    assert audits["natures-sanctuary"].automated is True

    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)
