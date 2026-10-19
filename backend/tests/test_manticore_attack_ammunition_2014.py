"""2014 printed attack ammunition is universal, finite and fight-local."""
from __future__ import annotations

import logging

import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.attack_action_sequences import select_sequence
from app.combat.attacks import resolve_attack
from app.combat.pit_policy import choose_standard_attack
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_attack_ammunition_2014 import attack_ammunition_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition

logger = logging.getLogger(__name__)


class FixedDice:
    def __init__(self, d20=15):
        self.d20 = d20
        self.calls = []

    def roll(self, sides):
        self.calls.append(sides)
        return self.d20 if sides == 20 else 1


def _monster(name):
    return next(row for row in load_monster_source_2014() if row.id == name)


def _setup(distance=20):
    card = compile_combatant(adapt_basic_monster_2014(_monster("manticore")))
    target_card = compile_combatant(adapt_basic_monster_2014(_monster("commoner"))).model_copy(update={"max_hp": 200})
    attacker = EncounterCombatant(combatant_id="attacker", side="monsters", position_ft=0,
                                 state=build_combatant_state(card))
    target = EncounterCombatant(combatant_id="target", side="heroes", position_ft=0,
                               state=build_combatant_state(target_card))
    attacker.state.position = GridPosition(x=6, y=6)
    target.state.position = GridPosition(x=6-distance//5, y=6)
    attacker.state.formation_row = "back"
    setup = EncounterSetup(heroes=[target], monsters=[attacker],
                           hero_total_levels=1, monster_total_cr="0", ruleset="2014")
    return attacker, target, setup


def test_source_ammunition_binding_and_immutable_card():
    try:
        source = _monster("manticore")
        before = source.model_dump()
        assert attack_ammunition_2014(source) == {"tail-spike": 24}
        assert basic_blockers_2014(source) == ()
        compiled = compile_combatant(adapt_basic_monster_2014(source))
        ammo = next(resource for resource in compiled.resources if resource.id == "tail-spike")
        assert ammo.max_uses == 24
        spike = next(attack for attack in [compiled.weapon_attack, *compiled.alternate_weapon_attacks]
                     if attack.id == "2014-manticore-tail-spike")
        assert spike.resource_id == "tail-spike" and spike.resource_cost == 1
        assert [(variant.attack_kind.value, [slot.attack_ids for slot in variant.slots])
                for variant in compiled.attack_action.variants] == [
                    ("melee", [["2014-manticore-bite"], ["2014-manticore-claw"], ["2014-manticore-claw"]]),
                    ("ranged", [["2014-manticore-tail-spike"]] * 3),
                ]
        assert source.model_dump() == before
    except Exception:
        logger.exception("Manticore source-ammunition binding failed.")
        raise


@pytest.mark.parametrize("mutation", ["count", "trait", "source", "slots"])
def test_mutated_ammunition_source_fails_closed(mutation):
    source = _monster("manticore").model_copy(deep=True)
    if mutation == "count":
        source.limited_action_uses["tail-spike"] = 23
    elif mutation == "trait":
        source.trait_names.remove("Tail Spike Regrowth")
    elif mutation == "source":
        source.source_traits = source.source_traits.replace("twenty-four", "twenty-three")
    else:
        source.multiattack_slots[1] = ["tail-spike"]
    assert basic_blockers_2014(source)


def test_three_shots_charge_three_uses_with_logs_and_new_fight_resets():
    try:
        actor, target, setup = _setup()
        assert select_sequence(actor, setup)[0].attack_kind.value == "ranged"
        dice = FixedDice()
        events, _ = resolve_attack_action(1, 1, actor, setup, dice)
        attacks = [e for e in events if e.event_type == "attack"]
        assert len(attacks) == 3
        assert [e.resource_remaining for e in attacks] == [23, 22, 21]
        assert all("ammunition remaining" in e.description for e in attacks)
        assert next(resource for resource in actor.state.resources if resource.id == "tail-spike").current_uses == 21
        fresh, _, _ = _setup()
        assert next(resource for resource in fresh.state.resources if resource.id == "tail-spike").current_uses == 24
    except Exception:
        logger.exception("Manticore three-shot resource accounting failed.")
        raise


def test_missed_attacks_spend_one_and_exhaustion_prevents_more_shots():
    actor, target, setup = _setup()
    attack = next(a for a in [actor.state.template.weapon_attack, *actor.state.template.alternate_weapon_attacks]
                  if a.id == "2014-manticore-tail-spike")
    resource = next(r for r in actor.state.resources if r.id == "tail-spike")
    resource.current_uses = 2
    assert select_sequence(actor, setup) is None  # Three-shot option cannot be fully funded.
    assert choose_standard_attack(actor, setup)[1].id == attack.id
    dice = FixedDice(d20=2)  # Miss, but NOT natural 1 (which would terminate the turn).
    first = resolve_attack(1, 1, actor.state, target.state, attack, 20, dice,
                           spend_action=False, close_enemy_active=False)
    assert not first.hit and first.resource_remaining == 1
    second = resolve_attack(2, 1, actor.state, target.state, attack, 20, dice,
                            spend_action=False, close_enemy_active=False)
    assert not second.hit and second.resource_remaining == 0
    assert choose_standard_attack(actor, setup) is None
    with pytest.raises(RuntimeError, match="Attack resolution failed"):
        resolve_attack(3, 1, actor.state, target.state, attack, 20, dice,
                       spend_action=False, close_enemy_active=False)
    assert resource.current_uses == 0
