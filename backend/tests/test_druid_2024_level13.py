from __future__ import annotations

from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_2024_druid_level_thirteen_binds_printed_fire_storm_cubes() -> None:
    hero = build_thalen_greenbough_level(13)
    profile = build_thalen_greenbough_profile(13)
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("druid", 13, "2024", 7)

    assert hero.level == 13
    assert hero.max_hp == 68
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
    assert package.spells[-1].spell_level == 7
    assert package.spells[-1].role == "damage"
    assert package.spells[-1].required_capabilities == ["save-damage", "area"]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["druid-combat-spells-7"].automated is True
    assert audits["druid-combat-spells-7"].combat_relevant is True

    storm = next(item for item in hero.spell_save_actions if item.id == "fire-storm")
    assert storm.damage_dice_count == 7
    assert storm.damage_dice_size == 10
    assert storm.damage_type == "fire"
    assert storm.area is not None
    assert storm.area.contiguous_section_count == 10
    assert storm.area.length_ft == 10
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)
