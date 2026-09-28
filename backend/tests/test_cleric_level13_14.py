from __future__ import annotations

from app.combat.damaging_action_riders import resolve_damaging_action_temporary_hp
from app.combat.spell_policy import spell_at_slot
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_high_profile import (
    build_seraphine_dawnshield_level13_profile,
    build_seraphine_dawnshield_level14_profile,
)
from app.content.audited_fighter import build_karnok_stoneward
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent


def _resources(template) -> dict[str, int]:
    try:
        return {item.id: item.max_uses for item in template.resources}
    except Exception as exc:
        raise AssertionError("Unable to inspect Cleric resources.") from exc


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    try:
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=position,
            state=build_combatant_state(template),
        )
    except Exception as exc:
        raise AssertionError(f"Unable to build encounter member {combatant_id}.") from exc


def test_level_thirteen_reuses_existing_upcast_mechanics() -> None:
    level12 = build_seraphine_dawnshield_level(12)
    hero = build_seraphine_dawnshield_level(13)
    profile = build_seraphine_dawnshield_level13_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 13)

    assert hero.max_hp == level12.max_hp + 5 == 68
    assert (hero.ability_scores.wisdom, hero.ability_scores.charisma) == (20, 17)
    assert _resources(hero)["spell-slot-7"] == 1
    assert _resources(hero)["channel-divinity"] == 3

    inflict = next(item for item in hero.spell_save_actions if item.id == "inflict-wounds-l6")
    scaled = spell_at_slot(inflict, 7)
    assert (scaled.damage_dice_count, scaled.damage_dice_size, scaled.damage_type) == (8, 10, "necrotic")

    healing = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds-l7")
    assert (healing.dice_count, healing.dice_size, healing.healing_bonus) == (7, 8, 14)
    assert healing.resource_id == "spell-slot-7"

    assert len(package.spells) == 17
    assert package.spells[-1].id == "fire-storm"
    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_fourteen_rider_can_choose_an_ally_within_sixty_feet() -> None:
    hero = build_seraphine_dawnshield_level(14)
    profile = build_seraphine_dawnshield_level14_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    cleric = _member(hero, "cleric", "heroes", 0)
    ally = _member(build_karnok_stoneward(), "ally", "heroes", 40)
    far_ally = _member(build_karnok_stoneward(), "far-ally", "heroes", 65)
    enemy = _member(build_karnok_stoneward(), "enemy", "monsters", 100)
    ally.state.current_hp = 1
    far_ally.state.current_hp = 1
    setup = EncounterSetup(
        heroes=[cleric, ally, far_ally],
        monsters=[enemy],
        hero_total_levels=16,
        monster_total_cr="1",
        ruleset="2024",
    )
    damage_event = BattleEvent(
        sequence=1,
        round_number=1,
        event_type="saving_throw",
        actor_id="cleric",
        actor_name=hero.name,
        target_id="enemy",
        target_name="Enemy",
        damage_components=[
            DamageRollComponent(
                source="Sacred Flame",
                notation="3d8+5",
                rolls=[1, 1, 1],
                modifier=5,
                damage_type="radiant",
                total=8,
                applied_total=8,
            ),
        ],
        description="Sacred Flame deals damage.",
    )

    rider = hero.progression_features.damaging_action_temporary_hp_rider
    assert rider is not None
    assert (rider.action_ids, rider.ability, rider.multiplier, rider.range_ft, rider.target_mode) == (
        ["sacred-flame"], "wisdom", 2, 60, "self_or_ally",
    )
    event = resolve_damaging_action_temporary_hp(
        2, 1, cleric, setup, "sacred-flame", [damage_event],
    )
    assert event is not None
    assert event.target_id == "ally"
    assert ally.state.temporary_hp == 10
    assert far_ally.state.temporary_hp == 0

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_certified_registry_exposes_cleric_levels_thirteen_and_fourteen() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 13, "canonical")][1] == "seraphine-dawnshield-l13"
    assert registry[("cleric", 14, "canonical")][1] == "seraphine-dawnshield-l14"
    assert ("cleric", 15, "canonical") not in registry
