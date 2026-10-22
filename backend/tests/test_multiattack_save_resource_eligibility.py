"""Finite-resource saving throw slots remain optional in Multiattack."""
from types import SimpleNamespace as NS
from unittest.mock import patch

from app.combat.attack_action_choices import save_choice
from app.domain.attack_action_definitions import AttackActionSlot


def test_exhausted_save_resource_skips_slot_and_restored_resource_enables_it():
    action = NS(id="spittle", range_ft=15, resource_id="spittle", resource_cost=1)
    actor = NS(combatant_id="actor", state=NS(template=NS(saving_throw_actions=[action])))
    target = NS(combatant_id="target", state=NS(grapple_sources=[]))
    slot = AttackActionSlot(save_action_ids=["spittle"])
    setup = NS(heroes=[actor], monsters=[target])
    with patch("app.combat.attack_action_choices.target_order", return_value=[target]), \
         patch("app.combat.attack_action_choices.save_distance", return_value=5), \
         patch("app.combat.attack_action_choices.legal_save_action", return_value=True), \
         patch("app.combat.attack_action_choices.resource_available", side_effect=[False, True]) as available:
        assert save_choice(actor, setup, slot) is None
        picked = save_choice(actor, setup, slot)
    assert picked[0] is target
    assert available.call_count == 2
