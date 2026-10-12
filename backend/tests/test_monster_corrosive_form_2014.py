from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.melee_hit_retaliation import apply_melee_hit_retaliation
from app.combat.state import build_combatant_state
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_heated_body_2014 import corrosive_form_retaliation_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant
from app.domain.weapons_base import DamageType
from scripts.browser_template_serializer import template_row


def _pudding():
    return next(monster for monster in load_monster_source_2014()
                if monster.id == "black-pudding")


def _member(template, ident, side, distance):
    return EncounterCombatant(
        combatant_id=ident, side=side, position_ft=distance,
        state=build_combatant_state(template),
    )


def _setup(*, resistances=(), immunities=()):
    source = _pudding()
    action = corrosive_form_retaliation_2014(source)[0]
    pudding_template = build_commoner().model_copy(update={
        "timed_self_buff_actions": [action],
        "max_hp": 100,
    })
    victim_template = build_commoner().model_copy(update={
        "max_hp": 100,
        "damage_resistances": list(resistances),
        "damage_immunities": list(immunities),
    })
    return (_member(victim_template, "attacker", "heroes", 5),
            _member(pudding_template, "pudding", "monsters", 0))


def test_printed_corrosive_form_is_passive_and_source_proven():
    source = _pudding()
    original = source.model_dump_json()
    assert "Corrosive Form" in source.trait_names
    result = corrosive_form_retaliation_2014(source)
    assert len(result) == 1
    action = result[0]
    assert action.id == "corrosive-form"
    assert action.activation_timing == "passive"
    assert action.duration_rounds is None and action.resource_id is None
    rule = action.melee_hit_retaliation
    assert (rule.range_ft, rule.dice_count, rule.dice_size,
            rule.damage_type, rule.on_contact) == (5, 1, 8, DamageType.ACID, True)
    assert "Corrosive Form" not in unsupported_traits_2014(source)
    # The independently source-proven Pseudopod is now admitted.
    assert "attack:incomplete" not in basic_blockers_2014(source)
    assert source.model_dump_json() == original


def test_source_mutations_fail_closed_instead_of_admitting_empty_trait():
    source = _pudding()
    altered = source.model_copy(update={
        "source_traits": (source.source_traits or "").replace(
            "<strong>Corrosive Form.</strong>",
            "<strong>Unbound Corrosive Form.</strong>",
        ),
    })
    assert not corrosive_form_retaliation_2014(altered)
    assert "Corrosive Form" in unsupported_traits_2014(altered)
    assert "source:trait" in basic_blockers_2014(altered)


def test_hit_at_five_feet_and_explicit_contact_are_distinct_single_triggers():
    victim, pudding = _setup()
    assert not pudding.state.timed_effects
    assert apply_melee_hit_retaliation(
        victim, pudding, melee=False, dice=FixedDiceProvider([8]),
    ) == 0
    assert victim.state.current_hp == 100
    assert apply_melee_hit_retaliation(
        victim, pudding, melee=True, dice=FixedDiceProvider([8]),
        affected_states=[victim.state, pudding.state],
    ) == 8
    assert victim.state.current_hp == 92
    assert apply_melee_hit_retaliation(
        victim, pudding, melee=False, physical_contact=True,
        dice=FixedDiceProvider([3]), affected_states=[victim.state],
    ) == 3
    assert victim.state.current_hp == 89
    victim.position_ft = 10
    assert apply_melee_hit_retaliation(
        victim, pudding, melee=True, dice=FixedDiceProvider([8]),
    ) == 0
    assert victim.state.current_hp == 89


def test_acid_resistance_and_immunity_use_existing_damage_defenses():
    victim, pudding = _setup(resistances=[DamageType.ACID])
    assert apply_melee_hit_retaliation(
        victim, pudding, melee=True, dice=FixedDiceProvider([7]),
        affected_states=[victim.state, pudding.state],
    ) == 3
    assert victim.state.current_hp == 97
    victim.state.template.damage_immunities.append(DamageType.ACID)
    assert apply_melee_hit_retaliation(
        victim, pudding, melee=True, dice=FixedDiceProvider([7]),
        affected_states=[victim.state, pudding.state],
    ) == 0
    assert victim.state.current_hp == 97


def test_browser_export_reuses_existing_passive_rule_shape():
    action = corrosive_form_retaliation_2014(_pudding())[0]
    template = build_commoner().model_copy(update={"timed_self_buff_actions": [action]})
    row = template_row(template)
    assert row["timed_self_buff_actions"][0]["meleeHitRetaliation"] == {
        "rangeFt": 5, "diceCount": 1, "diceSize": 8,
        "damageType": "acid", "onContact": True,
    }
