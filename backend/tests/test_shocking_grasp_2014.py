from __future__ import annotations

from app.combat.action_economy import is_available
from app.combat.dice import FixedDiceProvider
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import expire_start_of_turn_conditions
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def test_shocking_grasp_scales_and_declares_shared_hit_effects() -> None:
    level_one = next(
        action for action in build_nyra_emberveil_2014(1).spell_attack_actions
        if action.id == "shocking-grasp"
    )
    level_seventeen = next(
        action for action in build_nyra_emberveil_2014(17).spell_attack_actions
        if action.id == "shocking-grasp"
    )

    assert (level_one.damage_dice_count, level_one.damage_dice_size) == (1, 8)
    assert level_seventeen.damage_dice_count == 4
    assert level_one.attack_kind == "melee"
    assert level_one.range_ft == 5
    assert level_one.advantage_if_target_wearing_metal_armor is True
    assert len(level_one.on_hit_timed_effects) == 1
    effect = level_one.on_hit_timed_effects[0]
    assert effect.expiry_timing == "source_turn_start"
    assert effect.suppress_reactions is True


def test_shocking_grasp_has_advantage_against_metal_armor_and_suppresses_reactions() -> None:
    caster = _member(build_nyra_emberveil_2014(1), "nyra", "heroes", 0)
    target = _member(build_karnok_stoneward_2014(1), "karnok", "monsters", 5)
    setup = EncounterSetup(
        heroes=[caster], monsters=[target],
        hero_total_levels=1, monster_total_cr="0", ruleset="2014",
    )
    spell = next(action for action in caster.state.template.spell_attack_actions if action.id == "shocking-grasp")

    event = resolve_spell_attack(
        1, 1, caster, target, spell, setup, "1:nyra",
        FixedDiceProvider([1, 15, 4]),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.rolls == [1, 15]
    assert event.hit is True
    assert event.applied_condition_ids == ["reaction-suppressed"]
    assert is_available(target.state, "reaction") is False

    early, sequence = expire_start_of_turn_conditions(2, 1, caster, setup)
    assert early == []
    assert sequence == 2
    assert is_available(target.state, "reaction") is False

    expired, _ = expire_start_of_turn_conditions(2, 2, caster, setup)
    assert expired
    assert "reaction-suppressed" not in target.state.active_effect_ids
    assert is_available(target.state, "reaction") is True
