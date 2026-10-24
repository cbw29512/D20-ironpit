"""Clay Golem Haste runtime lifecycle through generic Bonus Action and Recharge engines."""
from __future__ import annotations

from app.combat.bonus_attacks import resolve_bonus_attack_grant
from app.combat.condition_lifecycle import resolve_source_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import effective_armor_class
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.start_turn import begin_turn_with_events
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.domain.models import RollMode
from test_2014_clay_golem_haste import _setup


def test_haste_bonus_slam_is_effect_gated_and_available_on_both_eligible_turns():
    try:
        _source_row, setup, golem, target = _setup()
        grant = next(
            item for item in golem.state.template.bonus_attack_grants
            if item.name == "Haste"
        )
        slam = next(
            attack
            for attack in [
                golem.state.template.weapon_attack,
                *golem.state.template.alternate_weapon_attacks,
            ]
            if attack.id == grant.attack_ids[0]
        )
        assert slam.weapon.name == "Slam"
        assert slam.on_hit_maximum_hp_save is not None

        blocked, sequence = resolve_bonus_attack_grant(
            1, 1, golem, setup, FixedDiceProvider([10]), "1:clay",
        )
        assert blocked == [] and sequence == 1
        assert golem.state.bonus_action_available is True

        action = next(
            item for item in golem.state.template.timed_self_buff_actions
            if item.id == "haste"
        )
        resolve_timed_self_buff(
            1, 1, golem, action,
            affected_states=[golem.state, target.state], setup=setup,
        )
        events, sequence = resolve_bonus_attack_grant(
            2, 1, golem, setup,
            FixedDiceProvider([10, 1, 1, 20]), "1:clay",
        )
        assert len(events) == 1
        assert events[0].feature_id == grant.id
        assert events[0].attack_name == "Slam"
        assert golem.state.bonus_action_available is False

        start_events, sequence = begin_turn_with_events(
            sequence, 2, golem.combatant_id, golem.state,
            FixedDiceProvider([4]), member=golem,
        )
        assert any(event.feature_id == "recharge:haste" for event in start_events)
        assert next(
            item for item in golem.state.resources if item.id == "haste"
        ).current_uses == 0
        assert "haste" in golem.state.active_effect_ids

        second, sequence = resolve_bonus_attack_grant(
            sequence, 2, golem, setup,
            FixedDiceProvider([10, 1, 1, 20]), "2:clay",
        )
        assert len(second) == 1
        assert second[0].attack_name == "Slam"
    except Exception:
        raise


def test_haste_expires_at_end_of_next_turn_and_recharge_five_restores_it():
    try:
        _source_row, setup, golem, target = _setup()
        action = next(
            item for item in golem.state.template.timed_self_buff_actions
            if item.id == "haste"
        )
        resolve_timed_self_buff(
            1, 1, golem, action,
            affected_states=[golem.state, target.state], setup=setup,
        )
        base_ac = golem.state.template.armor_class

        begin_turn_with_events(
            2, 2, golem.combatant_id, golem.state,
            FixedDiceProvider([4]), member=golem,
        )
        assert "haste" in golem.state.active_effect_ids
        assert effective_armor_class(golem.state) == base_ac + 2

        ended, _ = resolve_source_condition_timing(
            3, 2, golem, setup, "source_turn_end",
        )
        assert any(event.feature_id == "haste" for event in ended)
        assert "haste" not in golem.state.active_effect_ids
        assert effective_armor_class(golem.state) == base_ac
        assert saving_throw_mode(golem.state, "dexterity") is RollMode.NORMAL

        recharge_events, _ = begin_turn_with_events(
            4, 3, golem.combatant_id, golem.state,
            FixedDiceProvider([5]), member=golem,
        )
        resource = next(item for item in golem.state.resources if item.id == "haste")
        assert resource.current_uses == 1
        assert any(
            event.feature_id == "recharge:haste"
            and event.resource_remaining == 1
            for event in recharge_events
        )

        fresh = build_combatant_state(golem.state.template)
        assert next(
            item for item in fresh.resources if item.id == "haste"
        ).current_uses == 1
        assert "haste" not in fresh.active_effect_ids
    except Exception:
        raise
