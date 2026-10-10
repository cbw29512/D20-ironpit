from __future__ import annotations

import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.melee_hit_retaliation import apply_melee_hit_retaliation
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_heated_body_2014 import heated_body_retaliation_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant
from app.domain.timed_self_buffs import MeleeHitRetaliation, TimedSelfBuffAction
from app.domain.weapons_base import DamageType
from scripts.browser_template_serializer import template_row


def _source(monster_id):
    return next(m for m in load_monster_source_2014() if m.id == monster_id)


def _member(template, combatant_id, side, position):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


@pytest.mark.parametrize("identity,dice", [
    ("azer", (1, 10)),
    ("salamander", (2, 6)),
    ("remorhaz", (3, 6)),
])
def test_heated_body_binds_exact_printed_dice_and_reach(identity, dice):
    m = _source(identity)
    before = m.model_dump_json()
    actions = heated_body_retaliation_2014(m)
    assert len(actions) == 1
    action = actions[0]
    assert action.name == "Heated Body" and action.activation_timing == "passive"
    assert action.resource_id is None and not action.concentration and action.duration_rounds is None
    assert action.melee_hit_retaliation.on_contact is True
    assert (
        action.melee_hit_retaliation.dice_count,
        action.melee_hit_retaliation.dice_size,
        action.melee_hit_retaliation.range_ft,
        action.melee_hit_retaliation.damage_type,
    ) == (*dice, 5, DamageType.FIRE)
    assert "Heated Body" not in unsupported_traits_2014(m)
    assert m.model_dump_json() == before


def test_azer_is_source_admitted_with_passive_and_correct_browser_binding():
    m = _source("azer")
    assert basic_blockers_2014(m) == ()
    template = compile_combatant(adapt_basic_monster_2014(m))
    action = next(a for a in template.timed_self_buff_actions if a.id == "heated-body")
    assert action.activation_timing == "passive"
    row = template_row(template)
    row_action = next(a for a in row["timed_self_buff_actions"] if a["id"] == "heated-body")
    assert row_action["meleeHitRetaliation"] == {
        "rangeFt": 5, "diceCount": 1, "diceSize": 10, "damageType": "fire", "onContact": True,
    }
    assert not any(r.id == "heated-body" for r in template.resources)


def test_azer_melee_hit_at_five_feet_passively_retaliates_and_ten_feet_does_not():
    azer = _member(compile_combatant(adapt_basic_monster_2014(_source("azer"))), "azer", "monsters", 0)
    attacker_template = build_commoner().model_copy(update={"max_hp": 100})
    attacker = _member(attacker_template, "attacker", "heroes", 5)
    assert not azer.state.timed_effects and not azer.state.active_effect_ids
    applied = apply_melee_hit_retaliation(
        attacker, azer, melee=True, dice=FixedDiceProvider([10]),
        affected_states=[azer.state, attacker.state],
    )
    assert applied == 10 and attacker.state.current_hp == 90
    attacker.position_ft = 10
    assert apply_melee_hit_retaliation(
        attacker, azer, melee=True, dice=FixedDiceProvider([1]),
    ) == 0
    assert attacker.state.current_hp == 90
    assert apply_melee_hit_retaliation(
        attacker, azer, melee=False, dice=FixedDiceProvider([1]),
    ) == 0


def test_heated_body_contact_only_requires_explicit_genuine_contact_and_defenses():
    azer = _member(compile_combatant(adapt_basic_monster_2014(_source("azer"))), "azer", "monsters", 0)
    commoner = build_commoner().model_copy(update={"max_hp": 100, "damage_resistances": [DamageType.FIRE]})
    attacker = _member(commoner, "attacker", "heroes", 5)
    assert apply_melee_hit_retaliation(
        attacker, azer, melee=False, physical_contact=False, dice=FixedDiceProvider([1]),
    ) == 0
    assert apply_melee_hit_retaliation(
        attacker, azer, melee=False, physical_contact=True, dice=FixedDiceProvider([9]),
        affected_states=[attacker.state],
    ) == 4
    assert attacker.state.current_hp == 96
    attacker.state.template.damage_immunities.append(DamageType.FIRE)
    assert apply_melee_hit_retaliation(
        attacker, azer, melee=False, physical_contact=True, dice=FixedDiceProvider([8]),
        affected_states=[attacker.state],
    ) == 0
    assert attacker.state.current_hp == 96


def test_heated_body_source_mutations_fail_closed():
    m = _source("azer")
    for bad in (
        m.source_traits.replace("touches the azer", "smells the azer"),
        m.source_traits.replace("5 feet", "nearby"),
        m.source_traits.replace("1d10", "unknown"),
    ):
        corrupted = m.model_copy(update={"source_traits": bad})
        assert not heated_body_retaliation_2014(corrupted)
        assert "source:trait" in basic_blockers_2014(corrupted)


def test_distinct_passive_and_active_retaliation_sources_both_trigger_once():
    """An existing timed source cannot shadow the monster's passive typed effect."""
    azer_template = compile_combatant(adapt_basic_monster_2014(_source("azer")))
    shield = TimedSelfBuffAction(
        id="shield-test", name="Fire Shield", action_cost="action",
        melee_hit_retaliation=MeleeHitRetaliation(
            range_ft=5, dice_count=2, dice_size=8, damage_type=DamageType.COLD,
        ),
    )
    combined = azer_template.model_copy(update={
        "timed_self_buff_actions": [*azer_template.timed_self_buff_actions, shield],
    })
    defender = _member(combined, "defender", "monsters", 0)
    # The timed Fire Shield effect is active in fight state, unlike a passive.
    from app.domain.timed_effects import TimedEffect
    defender.state.timed_effects.append(TimedEffect(
        effect_id="shield-test", source_id="defender", source_effect_id="shield-test", expires_round=10,
    ))
    opponent = _member(build_commoner().model_copy(update={"max_hp": 100}), "opponent", "heroes", 5)
    assert apply_melee_hit_retaliation(
        opponent, defender, melee=True, dice=FixedDiceProvider([6, 3, 3]),
        affected_states=[opponent.state, defender.state],
    ) == 12
    assert opponent.state.current_hp == 88
    assert apply_melee_hit_retaliation(
        opponent, defender, melee=False, physical_contact=True, dice=FixedDiceProvider([4]),
        affected_states=[opponent.state, defender.state],
    ) == 4
    assert opponent.state.current_hp == 84

def test_no_retaliation_does_not_evaluate_unrelated_legacy_grid_geometry():
    """Ordinary hits must not fail on geometry only required by retaliation."""
    from app.domain.grid import GridPosition

    attacker = _member(build_commoner(), "attacker", "heroes", 5)
    defender = _member(build_commoner(), "defender", "monsters", 0)
    defender.state.position = GridPosition(x=0, y=0)
    assert attacker.state.position is None
    assert apply_melee_hit_retaliation(
        attacker, defender, melee=True, dice=FixedDiceProvider([]),
    ) == 0
