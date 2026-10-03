from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2024_combat_profile import build_aurelia_2024_combat_profiles
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(ally_position: int = 5) -> tuple[EncounterSetup, EncounterCombatant, EncounterCombatant]:
    paladin = _member(build_aurelia_brightshield_2024(10), "aurelia", "heroes", 0)
    ally = _member(build_kael_stillwater_2024(1), "kael", "heroes", ally_position)
    enemy = _member(
        build_commoner().model_copy(update={"ruleset": "2024"}),
        "commoner",
        "monsters",
        30,
    )
    return EncounterSetup(
        heroes=[paladin, ally],
        monsters=[enemy],
        hero_total_levels=11,
        monster_total_cr="0",
        ruleset="2024",
    ), paladin, ally


def test_2024_paladin_level_ten_progression_is_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(10)
    hero = build_aurelia_brightshield_2024(10)
    combat = next(
        item for item in build_aurelia_2024_combat_profiles() if item.level == 10
    )

    assert profile.final_ability_scores.strength == 20
    assert profile.final_ability_scores.charisma == 15
    assert (hero.max_hp, hero.armor_class) == (84, 19)
    assert hero.weapon_attack.attack_bonus == 9
    assert hero.weapon_attack.damage_bonus == 5
    assert hero.skill_bonuses["athletics"] == 9
    assert {item.id: item.max_uses for item in hero.resources} == {
        "lay-on-hands": 50,
        "spell-slot-1": 4,
        "paladins-smite-free-cast": 1,
        "channel-divinity": 2,
        "spell-slot-2": 3,
        "faithful-steed-free-cast": 1,
        "spell-slot-3": 2,
    }

    package = canonical_spell_package("paladin", 10, "2024", 2)
    assert package is not None
    assert [spell.id for spell in package.spells] == [
        "cure-wounds", "divine-favor", "bless", "searing-smite",
        "thunderous-smite", "shining-smite", "lesser-restoration",
        "aura-of-vitality", "blinding-smite",
    ]

    auras = {
        aura.source_id: aura
        for aura in hero.progression_features.friendly_condition_immunity_auras
    }
    assert set(auras) == {"aura-of-devotion-2024", "aura-of-courage-2024"}
    courage = auras["aura-of-courage-2024"]
    assert (
        courage.source_name,
        courage.radius_ft,
        courage.condition_id,
        courage.inactive_while_incapacitated,
    ) == ("Aura of Courage", 10, "frightened", True)

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["aura-of-courage"].automated is True

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)


def test_2024_aura_of_courage_suppresses_frightened_only_inside_live_aura() -> None:
    setup, paladin, ally = _setup(ally_position=15)
    assert apply_timed_condition(ally.state, "frightened", "enemy-source") is not None
    assert "frightened" in ally.state.active_effect_ids

    sync_friendly_save_auras(setup)
    assert condition_is_immune(ally.state, "frightened") is False

    ally.position_ft = 5
    sync_friendly_save_auras(setup)
    assert "frightened" in ally.state.active_effect_ids
    assert condition_is_immune(ally.state, "frightened") is True

    ally.position_ft = 15
    sync_friendly_save_auras(setup)
    assert "frightened" in ally.state.active_effect_ids
    assert condition_is_immune(ally.state, "frightened") is False

    ally.position_ft = 5
    paladin.state.active_effect_ids.append("stunned")
    sync_friendly_save_auras(setup)
    assert condition_is_immune(ally.state, "frightened") is False


def test_level_nine_snapshot_remains_stable_after_level_ten() -> None:
    level9 = build_aurelia_brightshield_2024(9)
    assert level9.max_hp == 76
    assert level9.weapon_attack.attack_bonus == 9
    assert {
        aura.condition_id
        for aura in level9.progression_features.friendly_condition_immunity_auras
    } == {"charmed"}
