"""Full-source proof for form-qualified 2014 Charge and Pounce."""
from __future__ import annotations

import pytest

from app.combat.charge import resolve_charge_closing
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.state import begin_turn
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_form_qualified_charge_2014 import source_proven_form_qualified_charge_traits_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.models import EncounterSelection


def _monster(monster_id: str):
    return next(row for row in load_monster_source_2014() if row.id == monster_id)


def test_all_327_cards_find_exactly_two_form_qualified_charge_traits():
    applicable = {
        monster.id: source_proven_form_qualified_charge_traits_2014(monster)
        for monster in load_monster_source_2014()
        if source_proven_form_qualified_charge_traits_2014(monster)
    }
    assert applicable == {
        "wereboar": frozenset({"Charge (Boar or Hybrid Form Only)"}),
        "weretiger": frozenset({"Pounce (Tiger or Hybrid Form Only)"}),
    }


@pytest.mark.parametrize("monster_id", ("wereboar", "weretiger"))
def test_form_qualified_charge_is_bound_without_mutating_card(monster_id):
    monster = _monster(monster_id)
    before = monster.model_dump_json()
    labels = source_proven_form_qualified_charge_traits_2014(monster)
    assert labels
    assert labels.isdisjoint(unsupported_traits_2014(monster))
    assert basic_blockers_2014(monster) == ()
    assert monster.model_dump_json() == before


@pytest.mark.parametrize("monster_id,old,new", [
    ("wereboar", "DC 13 Strength", "DC 14 Strength"),
    ("weretiger", "at least 15 feet", "at least 20 feet"),
    ("weretiger", "one bite attack", "one claw attack"),
])
def test_form_qualified_charge_source_mutation_fails_closed(monster_id, old, new):
    monster = _monster(monster_id)
    assert old in monster.source_traits
    altered = monster.model_copy(update={
        "source_traits": monster.source_traits.replace(old, new),
    })
    assert not source_proven_form_qualified_charge_traits_2014(altered)
    assert "source:trait" in basic_blockers_2014(altered)


def test_card_identity_and_printed_heading_do_not_dispatch_runtime():
    monster = _monster("weretiger")
    renamed = monster.model_copy(update={"id": "renamed-card", "name": "Renamed Card"})
    assert source_proven_form_qualified_charge_traits_2014(renamed) == frozenset({
        "Pounce (Tiger or Hybrid Form Only)",
    })


def test_weretiger_pounce_resolves_source_attack_save_and_bonus_action_follow_up():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-2014-l5"],
        monster_ids=["2014-weretiger"],
        ruleset="2014",
    ))
    target, weretiger = setup.heroes[0], setup.monsters[0]
    weretiger.state.initiative_total = 20
    target.state.initiative_total = 10
    begin_turn(weretiger.state)
    source_before = _monster("weretiger").model_dump_json()

    events, _, handled = resolve_charge_closing(
        1, 1, weretiger, target,
        FixedDiceProvider([19, 4, 1, 19, 5, 6]), setup,
    )

    attacks = [event for event in events if event.event_type == "attack"]
    assert handled
    assert [event.feature_id for event in attacks] == ["charge", "charge-follow-up"]
    assert [event.weapon_id for event in attacks] == [
        "2014-weretiger-claw-tiger-or-hybrid-form-only",
        "2014-weretiger-bite-tiger-or-hybrid-form-only",
    ]
    assert "prone" in target.state.active_effect_ids
    assert weretiger.state.bonus_action_available is False
    assert _monster("weretiger").model_dump_json() == source_before

    fresh = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-2014-l5"],
        monster_ids=["2014-weretiger"], ruleset="2014",
    )).monsters[0]
    assert fresh.state.bonus_action_available is True
    assert fresh.state.active_effect_ids == []
