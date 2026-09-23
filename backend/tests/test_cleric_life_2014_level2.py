from app.combat.cleric_channel_divinity import resolve_turn_undead
from app.combat.cleric_channel_policy import choose_channel_divinity
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_2014_life_cleric_level_two_resources_and_fingerprint() -> None:
    hero = build_seraphine_dawnshield_2014(2)
    profile = build_seraphine_dawnshield_2014_profile(2)
    combat = build_seraphine_2014_combat_profile(2)

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 3,
        "channel-divinity": 1,
    }
    assert hero.max_hp == 19
    assert hero.progression_features.saving_throw_advantage_grants
    assert {spell.id for spell in hero.defensive_spell_actions} == {
        "bless", "shield-of-faith", "sanctuary",
    }
    sanctuary = next(spell for spell in hero.defensive_spell_actions if spell.id == "sanctuary")
    assert sanctuary.action_cost == "bonus_action"
    assert sanctuary.modifier_effects[0].kind == "targeting-save-gate"
    assert sanctuary.modifier_effects[0].save_dc == 13
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_2014_turn_undead_applies_trembling_and_repeats_save() -> None:
    cleric = _member(build_seraphine_dawnshield_2014(2), "cleric", "heroes", 0)
    skeleton = _member(build_combatant_from_capabilities("2014-skeleton"), "skeleton", "monsters", 10)
    setup = EncounterSetup(
        heroes=[cleric], monsters=[skeleton],
        hero_total_levels=2, monster_total_cr="1/4", ruleset="2014",
    )

    events, sequence = resolve_turn_undead(
        1, 1, cleric, setup, (skeleton,), FixedDiceProvider([1]),
    )

    assert sequence == 2
    assert events[0].save_succeeded is False
    assert events[0].applied_condition_ids == ["trembling"]
    assert "trembling" in skeleton.state.active_effect_ids
    assert "frightened" not in skeleton.state.active_effect_ids
    assert "incapacitated" not in skeleton.state.active_effect_ids
    assert next(item for item in cleric.state.resources if item.id == "channel-divinity").current_uses == 0

    begin_turn(skeleton.state)
    assert skeleton.state.action_available is False
    assert skeleton.state.bonus_action_available is False
    assert skeleton.state.reaction_available is False
    assert skeleton.state.movement_remaining_ft == 0

    lifecycle, _ = resolve_target_condition_timing(
        sequence, 1, skeleton, "target_turn_end", FixedDiceProvider([20]),
    )
    assert lifecycle[0].save_succeeded is True
    assert lifecycle[0].removed_condition_ids == ["trembling"]
    assert "trembling" not in skeleton.state.active_effect_ids


def test_2014_channel_divinity_never_falls_through_to_divine_spark() -> None:
    cleric = _member(build_seraphine_dawnshield_2014(2), "cleric", "heroes", 0)
    goblin = _member(build_combatant_from_capabilities("2014-goblin"), "goblin", "monsters", 10)
    for resource in cleric.state.resources:
        if resource.id.startswith("spell-slot-"):
            resource.current_uses = 0
    setup = EncounterSetup(
        heroes=[cleric], monsters=[goblin],
        hero_total_levels=2, monster_total_cr="1/4", ruleset="2014",
    )

    assert choose_channel_divinity(cleric, setup) is None
