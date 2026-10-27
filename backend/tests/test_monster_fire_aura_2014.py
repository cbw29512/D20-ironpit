from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.melee_hit_retaliation import apply_melee_hit_retaliation
from app.combat.state import build_combatant_state
from app.combat.timed_emanations import resolve_source_turn_start_emanations
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_fire_aura_2014 import fire_aura_action_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.weapons_base import DamageType
from scripts.browser_template_serializer import template_row


def _source(monster_id):
    return next(m for m in load_monster_source_2014() if m.id == monster_id)


def _member(template, combatant_id, side, position):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_balor_fire_aura_binds_exact_printed_parameters():
    m = _source("balor")
    before = m.model_dump_json()
    actions = fire_aura_action_2014(m)
    assert len(actions) == 1
    action = actions[0]
    assert action.name == "Fire Aura" and action.activation_timing == "passive"
    assert action.melee_hit_retaliation.on_contact is True
    assert (
        action.melee_hit_retaliation.dice_count,
        action.melee_hit_retaliation.dice_size,
        action.melee_hit_retaliation.range_ft,
        action.melee_hit_retaliation.damage_type,
    ) == (3, 6, 5, DamageType.FIRE)
    emanation = action.start_turn_emanation_damage
    assert emanation.trigger == "source_turn_start"
    assert (emanation.radius_ft, emanation.dice_count, emanation.dice_size, emanation.damage_type) == (
        5, 3, 6, DamageType.FIRE,
    )
    assert "Fire Aura" not in unsupported_traits_2014(m)
    assert m.model_dump_json() == before


def test_balor_fire_aura_browser_serialization():
    m = _source("balor")
    template = compile_combatant(adapt_basic_monster_2014(m))
    action = next(a for a in template.timed_self_buff_actions if a.id == "fire-aura")
    row = template_row(template)
    row_action = next(a for a in row["timed_self_buff_actions"] if a["id"] == "fire-aura")
    assert row_action["meleeHitRetaliation"]["onContact"] is True
    assert row_action["startTurnEmanationDamage"] == {
        "trigger": "source_turn_start",
        "radius_ft": 5,
        "fixed_damage": 0,
        "dice_count": 3,
        "dice_size": 6,
        "damage_type": "fire",
        "save_ability": None,
        "save_dc": None,
        "success_damage": "none",
        "speed_multiplier": 1.0,
    }


def test_balor_fire_aura_melee_hit_and_source_turn_start():
    balor = _member(compile_combatant(adapt_basic_monster_2014(_source("balor"))), "balor", "monsters", 0)
    hero_template = build_commoner().model_copy(update={"max_hp": 100})
    hero = _member(hero_template, "hero", "heroes", 5)
    applied = apply_melee_hit_retaliation(
        hero, balor, melee=True, dice=FixedDiceProvider([6, 6, 6]),
        affected_states=[balor.state, hero.state],
    )
    assert applied == 18 and hero.state.current_hp == 82
    hero.position_ft = 10
    assert apply_melee_hit_retaliation(
        hero, balor, melee=True, dice=FixedDiceProvider([6, 6, 6]),
        affected_states=[balor.state, hero.state],
    ) == 0
    hero.position_ft = 5
    setup = EncounterSetup(heroes=[hero], monsters=[balor])
    events, _ = resolve_source_turn_start_emanations(
        1, 1, balor, setup, FixedDiceProvider([6, 6, 6]),
    )
    assert len(events) == 1 and hero.state.current_hp == 64
