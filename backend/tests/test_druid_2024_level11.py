from __future__ import annotations

from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.healing_spell_effects import build_heal_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_2024_druid_level_eleven_prioritizes_heal() -> None:
    hero = build_thalen_greenbough_level(11)
    profile = build_thalen_greenbough_profile(11)
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("druid", 11, "2024", 6)

    assert hero.level == 11
    assert hero.max_hp == 58
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
        "spell-slot-6": 1,
        "wild-shape": 3,
        "wild-resurgence-slot-restore": 1,
        "natural-recovery-free-cast": 1,
    }

    assert package is not None
    assert len(package.cantrips) == 5
    assert len(package.spells) == 16
    assert package.spells[-1].id == "heal"

    heal = next(item for item in hero.healing_actions if item.id == "heal")
    assert heal.action_cost == "action"
    assert heal.range_ft == 60
    assert heal.target_mode == "self_or_ally"
    assert heal.dice_count == 0
    assert heal.healing_bonus == 70
    assert heal.resource_id == "spell-slot-6"
    assert heal.resource_cost == 1
    assert heal.removable_conditions == ["blinded", "deafened", "poisoned"]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["druid-combat-spells-6"].automated is True

    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_2024_heal_upcast_reuses_fixed_healing_primitive() -> None:
    heal_7 = build_heal_2024(7)

    assert heal_7.id == "heal-l7"
    assert heal_7.healing_bonus == 80
    assert heal_7.resource_id == "spell-slot-7"
    assert heal_7.removable_conditions == ["blinded", "deafened", "poisoned"]
