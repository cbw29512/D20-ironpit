"""2014 Bulette action: source-verified one-time initiative winner opener."""
from __future__ import annotations

import pytest

from app.combat.area_save_actions import choose_area_save, resolve_area_save
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_opening_area_saves_2014 import source_proven_opening_area_saves_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition


def _source():
    return next(row for row in load_monster_source_2014() if row.id == "bulette")


def _member(cid, side, x, y, template):
    member = EncounterCombatant(
        combatant_id=cid, side=side, position_ft=x * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    member.state.current_round = 1
    return member


def _scene():
    beast = compile_combatant(adapt_basic_monster_2014(_source()))
    actor = _member("source", "monsters", 1, 1, beast)
    hero = build_aurelia_brightshield_2014(1).model_copy(update={"max_hp": 100})
    first = _member("first", "heroes", 4, 1, hero)
    second = _member("second", "heroes", 5, 2, hero)
    outside = _member("outside", "heroes", 8, 4, hero)
    actor.state.initiative_total = 20
    for target in (first, second, outside):
        target.state.initiative_total = 10
    setup = EncounterSetup(
        heroes=[first, second, outside], monsters=[actor],
        hero_total_levels=3, monster_total_cr="5", ruleset="2014",
        map_definition=BattleMapDefinition(id="impact", width_squares=12, height_squares=12),
    )
    return actor, first, second, outside, setup


def test_pinned_card_binds_exact_damage_and_approved_opener_only():
    source = _source()
    actions = source_proven_opening_area_saves_2014(source)
    assert len(actions) == 1
    card = actions[0]
    assert card.opening_initiative_only and card.name == "Deadly Leap"
    assert card.target_scope == "all-other-creatures"
    assert (card.dc, card.save_ability_choices, card.range_ft) == (16, ["strength", "dexterity"], 30)
    assert card.area.shape == "square" and card.area.length_ft == 10
    assert [d.damage_type for d in card.damage_components] == ["bludgeoning", "slashing"]
    assert all((d.dice_count, d.dice_size, d.damage_bonus) == (3, 6, 4) for d in card.damage_components)
    assert card.success_damage == "half"
    assert card.failed_save_timed_effect.effect_id == "prone"
    assert basic_blockers_2014(source) == ()
    assert "Standing Leap" in source.trait_names
    assert "Deadly Leap" in source.source_actions and "pushed 5 feet" in source.source_actions
    for old, changed in (("DC 16", "DC 17"), ("Strength or Dexterity", "Dexterity"),
                         ("pushed 5 feet", "pushed 10 feet")):
        mutant = source.model_copy(update={"source_actions": source.source_actions.replace(old, changed)})
        assert source_proven_opening_area_saves_2014(mutant) == []
        assert "source:extra-action" in basic_blockers_2014(mutant)


def test_winner_has_square_opener_and_loser_or_later_round_has_bite_only():
    actor, first, second, outside, setup = _scene()
    assert choose_area_save(actor, setup) is None
    selected = choose_area_save(actor, setup, opening_only=True)
    assert selected is not None
    action, placement = selected
    assert set(placement.target_ids) == {"first", "second"}
    assert "outside" not in placement.target_ids
    assert placement.direction is None
    actor.state.initiative_total = 10
    assert choose_area_save(actor, setup, opening_only=True) is None
    with pytest.raises(ValueError, match="winning initiative"):
        resolve_area_save(1, 1, actor, setup, action, placement, FixedDiceProvider([1]))
    actor.state.initiative_total = 20
    actor.state.current_round = 2
    assert choose_area_save(actor, setup, opening_only=True) is None
    assert any(attack.name == "Bite" for attack in actor.state.template.attacks)


def test_opener_one_action_two_typed_components_independent_saves():
    actor, first, second, _, setup = _scene()
    selected = choose_area_save(actor, setup, opening_only=True)
    assert selected is not None
    # Shared six damage dice, then two independent target saves.
    events, _ = resolve_area_save(
        1, 1, actor, setup, selected[0], selected[1],
        FixedDiceProvider([3] * 6 + [1, 20]),
    )
    assert len(events) == 2
    assert [event.target_id for event in events] == ["first", "second"]
    assert [event.save_succeeded for event in events] == [False, True]
    assert "prone" in first.state.active_effect_ids
    assert "prone" not in second.state.active_effect_ids
    assert first.state.current_hp == 74  # 13 Bludgeoning + 13 Slashing
    assert second.state.current_hp == 88  # 6 + 6, each half rounded down
    assert all([part.damage_type.value for part in event.damage_components] ==
               ["bludgeoning", "slashing"] for event in events)
    assert actor.state.action_available is False
    assert selected[0].save_ability == "strength"
