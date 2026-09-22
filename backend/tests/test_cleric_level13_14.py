from app.combat.dice import FixedDiceProvider
from app.combat.spell_policy import SpellChoice
from app.combat.spell_resolution import resolve_spell
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_high_profile import (
    build_seraphine_dawnshield_level13_profile,
    build_seraphine_dawnshield_level14_profile,
)
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _resources(template) -> dict[str, int]:
    return {item.id: item.max_uses for item in template.resources}


def test_level_thirteen_uses_simple_seventh_level_upcasts() -> None:
    level12 = build_seraphine_dawnshield_level(12)
    hero = build_seraphine_dawnshield_level(13)
    profile = build_seraphine_dawnshield_level13_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 13)

    assert hero.max_hp == level12.max_hp + 5 == 68
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma) == (20, 17)
    assert _resources(hero) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "channel-divinity": 3,
        "divine-intervention": 1,
        "adrenaline-rush": 5,
        "relentless-endurance": 1,
    }

    damage = next(item for item in hero.spell_save_actions if item.id == "inflict-wounds-l7")
    healing = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds-l7")
    assert (damage.level, damage.damage_dice_count, damage.damage_dice_size) == (7, 8, 10)
    assert (damage.damage_type, damage.success_damage, damage.dc) == ("necrotic", "half", 18)
    assert (healing.dice_count, healing.dice_size, healing.healing_bonus) == (7, 8, 14)
    assert healing.resource_id == "spell-slot-7"

    assert len(package.spells) == 17
    assert package.spells[-1].id == "fire-storm"

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["cleric-combat-spells-7"].automated is True
    assert audits["inflict-wounds-upcast-l7"].automated is True
    assert audits["mass-cure-wounds-upcast-l7"].automated is True
    assert audits["fire-storm"].combat_relevant is False

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_fourteen_improved_blessed_strikes_uses_generic_temp_hp_rider() -> None:
    level13 = build_seraphine_dawnshield_level(13)
    hero = build_seraphine_dawnshield_level(14)
    profile = build_seraphine_dawnshield_level14_profile()
    combat = build_pregen_combat_profiles()[hero.id]

    assert hero.max_hp == level13.max_hp + 5 == 73
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma) == (20, 17)
    sacred_flame = next(item for item in hero.spell_save_actions if item.id == "sacred-flame")
    assert (sacred_flame.damage_dice_count, sacred_flame.damage_dice_size, sacred_flame.damage_bonus) == (3, 8, 5)
    assert sacred_flame.dc == 18

    rider = hero.progression_features.damaging_action_temporary_hp_rider
    assert rider is not None
    assert (rider.source_id, rider.action_ids, rider.ability, rider.multiplier) == (
        "improved-blessed-strikes", ["sacred-flame"], "wisdom", 2,
    )

    cleric = _member(hero, "cleric", "heroes", 0)
    enemy = _member(build_combatant_from_capabilities("srd-skeleton"), "enemy", "monsters", 30)
    setup = EncounterSetup(
        heroes=[cleric],
        monsters=[enemy],
        hero_total_levels=14,
        monster_total_cr="1/4",
        ruleset="2024",
    )
    choice = SpellChoice(
        action=sacred_flame,
        slot_level=0,
        target_ids=("enemy",),
    )
    events, _ = resolve_spell(
        1, 1, cleric, setup, choice, "1:cleric",
        FixedDiceProvider([1, 1, 1, 1]),
    )

    rider_event = next(event for event in events if event.feature_id == "improved-blessed-strikes")
    assert cleric.state.temporary_hp == 10
    assert (rider_event.temporary_hp_before, rider_event.temporary_hp_after) == (0, 10)

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["improved-blessed-strikes"].automated is True
    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_certified_registry_exposes_cleric_levels_thirteen_and_fourteen() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 13, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l13",
    )
    assert registry[("cleric", 14, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l14",
    )
    assert ("cleric", 15, "canonical") not in registry
