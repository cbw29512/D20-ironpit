from app.combat.action_economy import is_available
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.combat.turn_creature_effects import apply_turned_creature_effects
from app.combat.zero_hp import apply_damage
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=0,
        state=build_combatant_state(template),
    )


def _apply_trembling(cleric, skeleton, setup) -> None:
    applied = apply_turned_creature_effects(
        cleric, skeleton, setup, 1,
        source_effect_id="turn-undead",
        turned_effect_id="trembling",
        include_frightened=False,
        include_incapacitated=False,
        suppress_action=True,
        suppress_bonus_action=True,
        suppress_reactions=True,
        suppress_movement=True,
        turn_behavior="normal",
        repeat_save_ability="wisdom",
        repeat_save_dc=13,
        repeat_save_timing="target_turn_end",
        expires_rounds=None,
        expiry_timing=None,
        ends_if_source_incapacitated=False,
        ends_if_source_dead=False,
    )
    assert applied == ["trembling"]


def test_2014_turn_undead_trembling_suppresses_voluntary_turn() -> None:
    cleric = _member(build_seraphine_dawnshield_2014(1), "cleric", "heroes")
    skeleton = _member(build_combatant_from_capabilities("2014-skeleton"), "skeleton", "monsters")
    setup = EncounterSetup(
        heroes=[cleric], monsters=[skeleton],
        hero_total_levels=1, monster_total_cr="1/4", ruleset="2014",
    )
    _apply_trembling(cleric, skeleton, setup)

    assert "frightened" not in skeleton.state.active_effect_ids
    assert "incapacitated" not in skeleton.state.active_effect_ids
    begin_turn(skeleton.state)
    assert is_available(skeleton.state, "action") is False
    assert is_available(skeleton.state, "bonus_action") is False
    assert is_available(skeleton.state, "reaction") is False
    assert skeleton.state.movement_remaining_ft == 0

    effect = next(item for item in skeleton.state.timed_effects if item.effect_id == "trembling")
    assert effect.turn_behavior == "normal"
    assert effect.repeat_save_ability == "wisdom"
    assert effect.repeat_save_dc == 13
    assert effect.repeat_save_timing == "target_turn_end"
    assert effect.expires_round is None
    assert effect.ends_on_damage is True


def test_2014_trembling_ends_on_save_or_damage() -> None:
    cleric = _member(build_seraphine_dawnshield_2014(1), "cleric", "heroes")
    skeleton = _member(build_combatant_from_capabilities("2014-skeleton"), "skeleton", "monsters")
    setup = EncounterSetup(
        heroes=[cleric], monsters=[skeleton],
        hero_total_levels=1, monster_total_cr="1/4", ruleset="2014",
    )
    _apply_trembling(cleric, skeleton, setup)

    events, _ = resolve_target_condition_timing(
        1, 1, skeleton, "target_turn_end", FixedDiceProvider([20]),
    )
    assert events[0].save_succeeded is True
    assert events[0].removed_condition_ids == ["trembling"]
    assert "trembling" not in skeleton.state.active_effect_ids

    _apply_trembling(cleric, skeleton, setup)
    apply_damage(skeleton.state, 1)
    assert "trembling" not in skeleton.state.active_effect_ids
    assert not any(effect.effect_id == "trembling" for effect in skeleton.state.timed_effects)
