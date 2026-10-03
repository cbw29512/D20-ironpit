from __future__ import annotations

from app.combat.friendly_save_auras import sync_friendly_save_auras
from app.combat.modifier_stack import saving_throw_flat_bonus
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy
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


def _setup() -> tuple[EncounterSetup, EncounterCombatant, EncounterCombatant]:
    paladin = _member(build_aurelia_brightshield_2024(6), "aurelia", "heroes", 0)
    ally = _member(build_kael_stillwater_2024(1), "kael", "heroes", 5)
    enemy = _member(build_commoner(), "commoner", "monsters", 30)
    return EncounterSetup(
        heroes=[paladin, ally],
        monsters=[enemy],
        hero_total_levels=7,
        monster_total_cr="0",
        ruleset="2024",
    ), paladin, ally


def test_2024_paladin_level_six_progression_is_raw_ready() -> None:
    profile = build_aurelia_brightshield_2024_profile(6)
    hero = build_aurelia_brightshield_2024(6)
    combat = next(
        item for item in build_aurelia_2024_combat_profiles() if item.level == 6
    )

    assert profile.final_ability_scores.strength == 19
    assert profile.final_ability_scores.charisma == 14
    assert (hero.max_hp, hero.armor_class) == (52, 19)
    assert hero.weapon_attack.attack_bonus == 7
    assert hero.weapon_attack.damage_bonus == 4
    assert hero.skill_bonuses["athletics"] == 7
    assert {item.id: item.max_uses for item in hero.resources} == {
        "lay-on-hands": 30,
        "spell-slot-1": 4,
        "paladins-smite-free-cast": 1,
        "channel-divinity": 2,
        "spell-slot-2": 2,
        "faithful-steed-free-cast": 1,
    }

    aura = hero.progression_features.friendly_saving_throw_aura
    assert aura is not None
    assert (
        aura.source_id,
        aura.source_name,
        aura.radius_ft,
        aura.flat_bonus,
        aura.inactive_while_incapacitated,
        aura.inactive_while_unconscious,
    ) == ("aura-of-protection-2024", "Aura of Protection", 10, 2, True, False)

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["aura-of-protection"].automated is True

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)


def test_2024_aura_of_protection_uses_live_range_and_incapacitated_state() -> None:
    setup, paladin, ally = _setup()

    sync_friendly_save_auras(setup)
    assert saving_throw_flat_bonus(paladin.state) == 2
    assert saving_throw_flat_bonus(ally.state) == 2

    ally.position_ft = 15
    sync_friendly_save_auras(setup)
    assert saving_throw_flat_bonus(ally.state) == 0

    ally.position_ft = 5
    paladin.state.active_effect_ids.append("stunned")
    sync_friendly_save_auras(setup)
    assert saving_throw_flat_bonus(paladin.state) == 0
    assert saving_throw_flat_bonus(ally.state) == 0
