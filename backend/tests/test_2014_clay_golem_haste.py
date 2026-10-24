"""2014 Clay Golem Haste composed from universal timed-buff, recharge and bonus-attack primitives."""
from __future__ import annotations

from app.combat.modifier_stack import effective_armor_class, effective_speed
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.state import build_combatant_state
from app.combat.timed_self_buff_policy import choose_timed_self_buff_action
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_recharge_self_buffs_2014 import (
    recharge_self_buff_bindings_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode


def _source():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "clay-golem")
    except Exception as exc:
        raise AssertionError("Missing pinned 2014 Clay Golem") from exc


def _setup():
    try:
        source = _source()
        template = compile_combatant(adapt_basic_monster_2014(source))
        golem = EncounterCombatant(
            combatant_id="clay",
            side="monsters",
            position_ft=5,
            state=build_combatant_state(template),
        )
        target = EncounterCombatant(
            combatant_id="target",
            side="heroes",
            position_ft=0,
            state=build_combatant_state(
                build_demo_fighter().model_copy(update={"armor_class": 1, "max_hp": 100})
            ),
        )
        setup = EncounterSetup(
            heroes=[target],
            monsters=[golem],
            hero_total_levels=1,
            monster_total_cr=source.challenge_rating,
            ruleset="2014",
        )
        return source, setup, golem, target
    except Exception:
        raise


def test_source_proof_binds_exact_haste_composition_without_name_dispatch():
    try:
        source = _source()
        snapshot = source.model_dump_json()
        bindings = recharge_self_buff_bindings_2014(source)
        assert len(bindings) == 1
        binding = bindings[0]
        action = binding.action
        assert (action.id, action.name, action.action_cost) == ("haste", "Haste", "action")
        assert action.resource_id == "haste"
        assert action.duration_rounds == 1
        assert action.expiry_timing == "source_turn_end"
        assert action.magical_effect is True
        assert action.concentration is False
        assert action.movement_mode_grants == []
        assert len(action.modifier_effects) == 1
        assert (action.modifier_effects[0].kind, action.modifier_effects[0].flat_bonus) == (
            "armor-class", 2,
        )
        assert action.saving_throw_advantage_grants[0].abilities == ["dexterity"]
        assert (binding.resource.id, binding.resource.max_uses) == ("haste", 1)
        assert (binding.recharge.resource_id, binding.recharge.minimum_roll) == ("haste", 5)
        assert binding.bonus_attack_grant.required_active_effect_id == "haste"
        assert binding.bonus_attack_grant.attack_count == 1
        assert basic_blockers_2014(source) == ()
        assert source.model_dump_json() == snapshot
    except Exception:
        raise


def test_haste_spends_action_and_resource_then_grants_only_printed_benefits():
    try:
        _source_row, setup, golem, target = _setup()
        action = next(
            item for item in golem.state.template.timed_self_buff_actions
            if item.id == "haste"
        )
        assert {item.id for item in golem.state.template.timed_self_buff_actions} >= {
            "haste", "berserk",
        }
        assert choose_timed_self_buff_action(golem, setup) == action
        base_speed = effective_speed(golem.state)
        event = resolve_timed_self_buff(
            1, 1, golem, action,
            affected_states=[golem.state, target.state], setup=setup,
        )
        resource = next(item for item in golem.state.resources if item.id == "haste")
        assert event.feature_id == "haste"
        assert event.resource_remaining == 0
        assert resource.current_uses == 0
        assert golem.state.action_available is False
        assert golem.state.bonus_action_available is True
        assert "haste" in golem.state.active_effect_ids
        assert effective_armor_class(golem.state) == golem.state.template.armor_class + 2
        assert saving_throw_mode(golem.state, "dexterity") is RollMode.ADVANTAGE
        assert saving_throw_mode(golem.state, "constitution") is RollMode.NORMAL
        assert effective_speed(golem.state) == base_speed
        assert golem.state.concentration is None
    except Exception:
        raise

