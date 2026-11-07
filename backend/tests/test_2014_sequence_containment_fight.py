"""Real 2014 double-Slam containment through ordinary encounter paths."""
from __future__ import annotations

import logging

from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_swallow_action import resolve_swallow_action
from app.combat.grapple import apply_grapple
from app.combat.state import build_combatant_state
from app.combat.swallow_lifecycle import release_invalid_swallowed, source_turn_swallowed_damage
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)


def _scene(size=CreatureSize.MEDIUM):
    try:
        card = next(c for c in load_monster_source_2014() if c.id == "shambling-mound")
        original = card.model_dump_json()
        template = compile_combatant(adapt_basic_monster_2014(card))
        victim_template = build_demo_fighter().model_copy(update={
            "max_hp": 200, "armor_class": 5, "size": size,
        })
        source = EncounterCombatant(
            combatant_id="source", side="monsters", position_ft=0,
            state=build_combatant_state(template),
        )
        victim = EncounterCombatant(
            combatant_id="victim", side="heroes", position_ft=5,
            state=build_combatant_state(victim_template),
        )
        setup = EncounterSetup(
            heroes=[victim], monsters=[source], ruleset="2014",
            hero_total_levels=2, monster_total_cr="5",
        )
        return card, original, source, victim, setup
    except Exception:
        logger.exception("Failed 2014 source-bound double-Slam fight setup.")
        raise


def test_two_real_slam_hits_engulf_and_source_turn_save_damage_and_death_release():
    try:
        card, original, source, victim, setup = _scene()
        events, seq = resolve_attack_action(
            1, 1, source, setup, FixedDiceProvider([16, 2, 2, 16, 2, 2]),
        )
        attacks = [event for event in events if event.event_type == "attack"]
        assert len(attacks) == 2 and all(event.hit for event in attacks)
        engulf = next(event for event in events if event.feature_id == "Engulf")
        assert engulf.target_id == victim.combatant_id
        assert "Engulf" in engulf.description
        assert source.state.action_available is False
        assert victim.state.swallowed is not None
        record = victim.state.swallowed
        assert (record.source_name, record.damage_dice_count,
                record.damage_dice_size, record.damage_bonus) == ("Engulf", 2, 8, 4)
        assert record.cannot_breathe and record.moves_with_source
        assert not record.exit_prone
        assert {"blinded", "restrained"} <= set(victim.state.active_effect_ids)
        assert not victim.state.grapple_sources
        hp = victim.state.current_hp

        saved, seq = source_turn_swallowed_damage(
            seq, 2, source, setup, FixedDiceProvider([20]),
        )
        assert len(saved) == 1 and saved[0].save_succeeded is True
        assert saved[0].save_dc == 14 and saved[0].save_ability == "constitution"
        assert victim.state.current_hp == hp
        failed, seq = source_turn_swallowed_damage(
            seq, 3, source, setup, FixedDiceProvider([2, 2, 2]),
        )
        assert len(failed) == 1 and failed[0].save_succeeded is False
        assert failed[0].damage_components[0].total == 8
        assert victim.state.current_hp == hp - 8
        source.state.is_dead, source.state.is_alive, source.state.current_hp = True, False, 0
        assert release_invalid_swallowed(setup) == ["victim"]
        assert victim.state.swallowed is None
        assert "restrained" not in victim.state.active_effect_ids
        assert "blinded" not in victim.state.active_effect_ids
        assert "prone" not in victim.state.active_effect_ids
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("Live double-hit containment/save/release fight failed.")
        raise


def test_one_miss_or_illegal_target_size_does_not_contain():
    try:
        for size, rolls, hit_count in (
            (CreatureSize.MEDIUM, [16, 2, 2, 1], 1),
            (CreatureSize.LARGE, [16, 2, 2, 16, 2, 2], 2),
        ):
            _, _, source, victim, setup = _scene(size)
            events, _ = resolve_attack_action(
                1, 1, source, setup, FixedDiceProvider(rolls),
            )
            assert sum(event.event_type == "attack" and event.hit for event in events) == hit_count
            assert victim.state.swallowed is None
            assert not any(event.feature_id == "Engulf" for event in events)
    except Exception:
        logger.exception("One miss and overlarge containment exclusions failed.")
        raise


def test_preexisting_grapple_allows_printed_containment_action_without_new_attack():
    try:
        _, _, source, victim, setup = _scene()
        apply_grapple(victim.state, "source", 14, 5)
        outcome = resolve_swallow_action(
            1, 1, source, setup, FixedDiceProvider([]),
        )
        assert outcome is not None
        events, seq = outcome
        assert seq == 2 and len(events) == 1
        assert events[0].event_type == "feature"
        assert events[0].feature_id == "Engulf"
        assert victim.state.swallowed is not None
        assert not victim.state.grapple_sources
        assert not source.state.action_available
    except Exception:
        logger.exception("Held-target containment Action resolution failed.")
        raise
