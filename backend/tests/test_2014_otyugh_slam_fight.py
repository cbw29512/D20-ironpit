"""Real 2014 Otyugh source card resolves its held-target Slam via the shared engine."""
from __future__ import annotations

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, release_grapple
from app.combat.multi_target_save_actions import (
    choose_multi_target_save_action, resolve_multi_target_save_action,
)
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


@pytest.fixture
def fight():
    try:
        card = next(x for x in load_monster_source_2014() if x.id == "otyugh")
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        def member(cid, side):
            return EncounterCombatant(
                combatant_id=cid, side=side, position_ft=5,
                state=build_combatant_state(template.model_copy(deep=True)),
            )
        actor = member("source", "monsters")
        held_a, held_b, unrelated = (
            member("held-a", "heroes"),
            member("held-b", "heroes"),
            member("unrelated", "heroes"),
        )
        # Holding only lives in fight state, not any source combatant template.
        for member_ in (held_a, held_b):
            assert apply_grapple(member_.state, actor.combatant_id, 13, 10, restrains=True)
        apply_grapple(unrelated.state, "different-source", 13, 10, restrains=True)
        setup = EncounterSetup(
            heroes=[held_a, held_b, unrelated], monsters=[actor],
            hero_total_levels=3, monster_total_cr="2", ruleset="2014",
        )
        return actor, (held_a, held_b, unrelated), setup
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Otyugh real-source fight fixture failed")
        raise


def test_real_slam_shared_damage_individual_saves_and_stun(fight) -> None:
    actor, (first, second, excluded), setup = fight
    selection = choose_multi_target_save_action(actor, setup)
    assert selection is not None
    action, targets = selection
    assert action.name == "Tentacle Slam"
    assert action.requires_target_grappled_by_source
    assert [item.combatant_id for item in targets] == ["held-a", "held-b"]
    before = [item.state.current_hp for item in (first, second, excluded)]
    events, seq = resolve_multi_target_save_action(
        1, 1, actor, setup, FixedDiceProvider([3, 4, 1, 20]), selection,
    )
    assert len(events) == 2 and seq >= 3
    assert [event.target_id for event in events] == ["held-a", "held-b"]
    assert first.state.current_hp == before[0] - 10
    assert second.state.current_hp == before[1] - 5
    assert excluded.state.current_hp == before[2]
    assert "stunned" in first.state.active_effect_ids
    assert "stunned" not in second.state.active_effect_ids
    assert actor.state.action_available is False
    assert any(item.effect_id == "stunned" and item.expires_round == 2
               and item.expiry_timing == "source_turn_end"
               for item in first.state.timed_effects)


def test_release_and_unrelated_grapple_do_not_enable_slam(fight) -> None:
    actor, (first, second, excluded), setup = fight
    release_grapple(first.state, actor.combatant_id)
    selection = choose_multi_target_save_action(actor, setup)
    assert selection is not None
    assert [item.combatant_id for item in selection[1]] == ["held-b"]
    release_grapple(second.state, actor.combatant_id)
    assert choose_multi_target_save_action(actor, setup) is None
    assert actor.state.action_available
    assert any(x.source_id == "different-source" for x in excluded.state.grapple_sources)
