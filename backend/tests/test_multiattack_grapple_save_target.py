"""A grapple-gated follow-up must target the grappled creature, not any enemy."""
from types import SimpleNamespace as NS
from unittest.mock import patch

from app.combat.attack_action_choices import save_choice
from app.domain.attack_action_definitions import AttackActionSlot


def test_conditional_save_filters_non_grappled_targets():
    actor = NS(combatant_id="chuul", state=NS(template=NS(
        saving_throw_actions=[NS(id="tentacles", range_ft=10)])))
    unrelated = NS(combatant_id="unrelated", state=NS(grapple_sources=[]))
    grappled = NS(combatant_id="grappled", state=NS(
        grapple_sources=[NS(source_id="chuul")]))
    setup = NS(heroes=[unrelated, grappled], monsters=[actor])
    slot = AttackActionSlot(save_action_ids=["tentacles"], requires_source_grapple=True)
    with patch("app.combat.attack_action_choices.target_order", return_value=[unrelated, grappled]), \
         patch("app.combat.attack_action_choices.save_distance", return_value=5), \
         patch("app.combat.attack_action_choices.legal_save_action", return_value=True):
        picked = save_choice(actor, setup, slot)
    assert picked[0] is grappled


def test_grappled_by_someone_else_does_not_qualify():
    actor = NS(combatant_id="chuul", state=NS(template=NS(
        saving_throw_actions=[NS(id="tentacles", range_ft=10)])))
    target = NS(combatant_id="target", state=NS(
        grapple_sources=[NS(source_id="another-monster")]))
    slot = AttackActionSlot(save_action_ids=["tentacles"], requires_source_grapple=True)
    with patch("app.combat.attack_action_choices.target_order", return_value=[target]):
        assert save_choice(actor, NS(heroes=[target], monsters=[actor]), slot) is None
