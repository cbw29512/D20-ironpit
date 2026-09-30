from __future__ import annotations

from app.combat.precombat_spells import prepare_defenses
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.demo import build_goblin_warrior
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _resource(member: EncounterCombatant, resource_id: str) -> int:
    return next(item.current_uses for item in member.state.resources if item.id == resource_id)


def test_2024_druid_level_seventeen_adds_foresight_and_ninth_level_slot() -> None:
    hero = build_thalen_greenbough_level(17)
    profile = build_thalen_greenbough_profile(17)
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("druid", 17, "2024", 5)

    assert hero.level == 17
    assert hero.max_hp == 88
    assert hero.ability_scores.wisdom == 20
    assert hero.ability_scores.charisma == 20
    assert hero.saving_throw_bonuses["wisdom"] == 11
    assert hero.saving_throw_bonuses["intelligence"] == 7
    assert hero.skill_bonuses["nature"] == 12
    assert hero.skill_bonuses["survival"] == 11
    assert hero.skill_bonuses["perception"] == 11

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
        "wild-shape": 4,
        "wild-resurgence-slot-restore": 1,
        "natural-recovery-free-cast": 1,
    }

    assert package is not None
    assert len(package.spells) == 19
    assert package.spells[-1].id == "foresight"

    foresight = next(item for item in hero.defensive_spell_actions if item.id == "foresight")
    assert (
        foresight.level,
        foresight.action_cost,
        foresight.range_ft,
        foresight.duration_minutes,
        foresight.target_policy,
        foresight.concentration,
        foresight.free_opening_cast,
    ) == (9, "action", 5, 480, "self", False, True)
    assert {item.kind for item in foresight.modifier_effects} == {
        "d20-test-advantage",
        "attacks-against-disadvantage",
    }

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["druid-combat-spells-9"].automated is True
    assert audits["druid-combat-spells-9"].combat_relevant is True

    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_2024_druid_foresight_is_free_opening_buff_but_requires_level_nine_slot() -> None:
    hero = EncounterCombatant(
        combatant_id="thalen",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_thalen_greenbough_level(17)),
    )
    enemy = EncounterCombatant(
        combatant_id="goblin",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(build_goblin_warrior()),
    )
    setup = EncounterSetup(
        heroes=[hero],
        monsters=[enemy],
        hero_total_levels=17,
        monster_total_cr="1/4",
    )

    assert _resource(hero, "spell-slot-9") == 1
    events, sequence = prepare_defenses(setup)

    assert sequence == 2
    assert len(events) == 1
    assert events[0].feature_id == "foresight"
    assert events[0].resource_remaining == 1
    assert "free opening buff" in events[0].description
    assert _resource(hero, "spell-slot-9") == 1
    assert hero.state.opening_buff_id == "foresight"
    assert "foresight" in hero.state.active_buff_effect_ids
    assert hero.state.concentration is None
    assert hero.state.action_available is True
    assert {
        (item.kind.value, item.source_effect_id, item.source_name)
        for item in hero.state.active_modifiers
        if item.source_effect_id == "foresight"
    } == {
        ("d20-test-advantage", "foresight", "Foresight"),
        ("attacks-against-disadvantage", "foresight", "Foresight"),
    }
