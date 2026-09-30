from __future__ import annotations

from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_2024_druid_level_fifteen_adds_improved_elemental_fury_and_sunburst() -> None:
    hero = build_thalen_greenbough_level(15)
    profile = build_thalen_greenbough_profile(15)
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("druid", 15, "2024", 5)

    assert hero.level == 15
    assert hero.max_hp == 78
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
        "spell-slot-8": 1,
        "wild-shape": 3,
        "wild-resurgence-slot-restore": 1,
        "natural-recovery-free-cast": 1,
    }

    assert package is not None
    assert len(package.spells) == 18
    assert package.spells[-1].id == "sunburst"
    assert package.spells[-1].spell_level == 8
    assert package.spells[-1].role == "damage"
    assert package.spells[-1].required_capabilities == [
        "save-damage",
        "area",
        "condition",
    ]

    spell_attacks = {item.id: item for item in hero.spell_attack_actions}
    assert spell_attacks["poison-spray"].range_ft == 330
    assert spell_attacks["fire-bolt"].range_ft == 420
    assert spell_attacks["starry-wisp"].range_ft == 360

    thunderclap = next(item for item in hero.spell_save_actions if item.id == "thunderclap")
    assert thunderclap.level == 0
    assert thunderclap.range_ft == 0

    previous = build_thalen_greenbough_level(14)
    previous_attacks = {item.id: item for item in previous.spell_attack_actions}
    assert previous_attacks["poison-spray"].range_ft == 30
    assert previous_attacks["fire-bolt"].range_ft == 120
    assert previous_attacks["starry-wisp"].range_ft == 60

    sunburst = next(item for item in hero.spell_save_actions if item.id == "sunburst")
    assert sunburst.dc == 18
    assert sunburst.level == 8
    assert sunburst.action_cost == "action"
    assert sunburst.range_ft == 150
    assert sunburst.area is not None
    assert (sunburst.area.shape, sunburst.area.origin, sunburst.area.radius_ft) == (
        "radius",
        "point",
        60,
    )
    assert sunburst.save_ability == "constitution"
    assert (sunburst.damage_dice_count, sunburst.damage_dice_size) == (12, 6)
    assert sunburst.damage_type == "radiant"
    assert sunburst.success_damage == "half"
    rider = sunburst.failed_save_timed_effect
    assert rider is not None
    assert rider.effect_id == "blinded"
    assert rider.duration_rounds == 10
    assert rider.repeat_save_ability == "constitution"
    assert rider.repeat_save_dc == 18
    assert rider.repeat_save_timing == "target_turn_end"

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["improved-elemental-fury-potent-spellcasting"].automated is True
    assert audits["improved-elemental-fury-potent-spellcasting"].combat_relevant is True
    assert audits["druid-combat-spells-8"].automated is True
    assert audits["druid-combat-spells-8"].combat_relevant is True

    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)
