"""2014 Chain attack: shared grapple source owns exactly one periodic Piercing tick."""
from __future__ import annotations

import pytest

from app.combat.attacks import resolve_attack
from app.combat.conditions import apply_hit_conditions
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import release_grapple
from app.combat.grapple_periodic_damage import grapple_turn_start_damage
from app.combat.start_of_turn_save_condition_events import resolve_start_of_turn_save_condition_damage_events
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_grapple_periodic_2014 import (
    source_grapple_periodic_proof_2014, supports_grapple_periodic_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType


def _source():
    return next(item for item in load_monster_source_2014() if item.id == "chain-devil")


def _combatants(immune=False):
    monster = _source()
    attack = compile_attack(_attack(monster, monster.attacks[0]))
    attacker = EncounterCombatant(
        combatant_id="chain-devil", side="monsters", position_ft=0,
        state=build_combatant_state(build_commoner()),
    )
    target_template = build_commoner().model_copy(
        update={"max_hp": 50, "damage_immunities": [DamageType.PIERCING] if immune else []},
    )
    target = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=5,
        state=build_combatant_state(target_template),
    )
    another = EncounterCombatant(
        combatant_id="other", side="heroes", position_ft=5,
        state=build_combatant_state(build_commoner()),
    )
    setup = EncounterSetup(
        heroes=[target, another], monsters=[attacker],
        hero_total_levels=2, monster_total_cr="8", ruleset="2014",
    )
    return attack, attacker, target, another, setup


def test_pinned_chain_source_uses_one_existing_grapple_rider_without_altering_card():
    monster = _source()
    before = monster.model_dump_json()
    attack_source = monster.attacks[0]
    assert source_grapple_periodic_proof_2014(monster, attack_source)
    assert supports_grapple_periodic_2014(attack_source)
    assert "source:extra-action" in basic_blockers_2014(monster)
    assert "source:reaction" in basic_blockers_2014(monster)
    attack = compile_attack(_attack(monster, attack_source))
    assert (attack.attack_bonus, attack.weapon.reach_ft, attack.weapon.dice_count,
            attack.weapon.dice_size, attack.damage_bonus) == (8, 10, 2, 6, 4)
    assert attack.forbid_target_grappled_by_self is False
    control = attack.control_effect
    assert control.grapple_escape_dc == 14 and control.restrains_while_grappled
    assert control.grapple_requires_source_free
    assert (control.grapple_periodic_damage.source_name, control.grapple_periodic_damage.dice_count,
            control.grapple_periodic_damage.dice_size, control.grapple_periodic_damage.damage_type) == (
                "Chain grapple", 2, 6, "piercing",
            )
    assert monster.multiattack_slots == [["chain"], ["chain"]]
    assert monster.model_dump_json() == before


def test_malformed_chain_source_fails_closed():
    monster = _source()
    attack = monster.attacks[0].model_copy(update={"ongoing_damage_effect": {
        **monster.attacks[0].ongoing_damage_effect, "damage_type": "force",
    }})
    with pytest.raises(ValueError, match="pinned source"):
        source_grapple_periodic_proof_2014(monster, attack)
    # Altering the canonical source text without changing the structured row is rejected.
    mutated = monster.model_copy(update={
        "source_actions": (monster.source_actions or "").replace("start of each of its turns", "end of each turn"),
    })
    with pytest.raises(ValueError, match="pinned source"):
        source_grapple_periodic_proof_2014(mutated, monster.attacks[0])
    malformed = attack.model_copy(update={"ongoing_damage_effect": {
        **attack.ongoing_damage_effect, "ends_when_grapple_source_ends": False,
    }})
    assert not supports_grapple_periodic_2014(malformed)


def test_one_active_chain_grapple_is_restrained_and_other_hits_remain_legal():
    attack, monster, target, other, setup = _combatants()
    applied = apply_hit_conditions(
        attack, target.state, monster.combatant_id, source_template=monster.state.template, setup=setup,
    )
    assert applied == ["grappled", "restrained"]
    assert len(target.state.grapple_sources) == 1
    assert target.state.grapple_sources[0].escape_dc == 14
    assert target.state.grapple_sources[0].periodic_damage.source_name == "Chain grapple"
    second = resolve_attack(
        1, 1, monster.state, other.state, attack, 5, FixedDiceProvider([18, 3, 4]),
        actor_event_id=monster.combatant_id, target_event_id=other.combatant_id,
        spend_action=False, turn_key="1:chain-devil", reaction_setup=setup,
        reaction_roller=monster,
    )
    assert second.hit
    assert other.state.grapple_sources == []  # Attack damage still resolves, no second grapple.


def test_chain_damage_ticks_on_victim_turn_only_while_owned_grapple_exists():
    attack, monster, target, other, setup = _combatants()
    apply_hit_conditions(attack, target.state, monster.combatant_id, setup=setup)
    assert grapple_turn_start_damage(target, setup, FixedDiceProvider([3, 4])) == [
        ("Chain grapple", 7, "piercing"),
    ]
    before = target.state.current_hp
    events, sequence = resolve_start_of_turn_save_condition_damage_events(
        1, 2, target, setup, FixedDiceProvider([3, 4]),
    )
    assert sequence > 1
    assert target.state.current_hp == before - 7
    assert any(event.feature_id == "Chain grapple" for event in events)
    release_grapple(target.state, monster.combatant_id)
    assert grapple_turn_start_damage(target, setup, FixedDiceProvider([1])) == []
    assert target.state.grapple_sources == []
    assert "restrained" not in target.state.active_effect_ids


def test_chain_periodic_damage_uses_shared_immunity_and_does_not_survive_source_death():
    attack, monster, target, _, setup = _combatants(immune=True)
    apply_hit_conditions(attack, target.state, monster.combatant_id, setup=setup)
    before = target.state.current_hp
    events, _ = resolve_start_of_turn_save_condition_damage_events(
        1, 2, target, setup, FixedDiceProvider([4, 5]),
    )
    assert target.state.current_hp == before
    assert any("deals 0 piercing" in event.description for event in events)
    monster.state.is_dead = True
    assert grapple_turn_start_damage(target, setup, FixedDiceProvider([1])) == []
