from __future__ import annotations

from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_2024_druid_level_ten_reuses_universal_defenses_and_damage_spell() -> None:
    hero = build_thalen_greenbough_level(10)
    profile = build_thalen_greenbough_profile(10)
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("druid", 10, "2024", 5)

    assert hero.level == 10
    assert hero.max_hp == 53
    assert hero.ability_scores.wisdom == 20
    assert hero.saving_throw_bonuses["wisdom"] == 9
    assert hero.skill_bonuses["nature"] == 10
    assert hero.damage_resistances == ["fire"]
    assert hero.condition_immunities == ["poisoned"]

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "wild-shape": 3,
        "wild-resurgence-slot-restore": 1,
        "natural-recovery-free-cast": 1,
    }

    assert package is not None
    assert len(package.spells) == 15
    assert package.spells[-1].id == "thunderwave"

    thunderwave = next(item for item in hero.spell_save_actions if item.id == "thunderwave")
    assert thunderwave.level == 1
    assert thunderwave.save_ability == "constitution"
    assert thunderwave.damage_dice_count == 2
    assert thunderwave.damage_dice_size == 8
    assert thunderwave.damage_type == "thunder"
    assert thunderwave.success_damage == "half"
    assert thunderwave.upcast_dice_per_level == 1
    assert thunderwave.failed_save_push_ft == 10
    assert thunderwave.area is not None
    assert thunderwave.area.shape == "cube"
    assert thunderwave.area.origin == "self"
    assert thunderwave.area.length_ft == 15

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["natures-ward"].automated is True
    assert audits["druid-combat-spell-l10"].automated is True

    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)
