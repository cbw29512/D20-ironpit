"""Generic Multiattack slots must evaluate grapple ownership from live fight state."""
from types import SimpleNamespace as NS

from app.combat.attack_action_choices import slot_grapple_eligible
from app.domain.attack_action_definitions import AttackActionSlot


def _member(identity, *, grapple_sources=(), dead=False):
    return NS(combatant_id=identity, state=NS(
        grapple_sources=list(grapple_sources), is_dead=dead,
    ))


def test_conditional_slot_tracks_grapple_added_and_removed_between_attacks():
    actor = _member("attacker")
    target = _member("target")
    setup = NS(heroes=[actor], monsters=[target])
    slot = AttackActionSlot(attack_ids=["pincer"], requires_source_grapple=True)
    assert not slot_grapple_eligible(actor, setup, slot)

    # A successful preceding attack creates a grapple in mutable battle state.
    target.state.grapple_sources.append(NS(source_id="attacker"))
    assert slot_grapple_eligible(actor, setup, slot)

    # A later escape or source change must be reflected immediately.
    target.state.grapple_sources[:] = [NS(source_id="other")]
    assert not slot_grapple_eligible(actor, setup, slot)


def test_grapple_must_belong_to_actor_and_target_must_be_alive():
    actor = _member("attacker")
    target = _member("target", grapple_sources=[NS(source_id="other")])
    setup = NS(heroes=[actor], monsters=[target])
    conditional = AttackActionSlot(save_action_ids=["tentacles"], requires_source_grapple=True)
    ordinary = AttackActionSlot(attack_ids=["pincer"])
    assert slot_grapple_eligible(actor, setup, ordinary)
    assert not slot_grapple_eligible(actor, setup, conditional)

    target.state.grapple_sources.append(NS(source_id="attacker"))
    target.state.is_dead = True
    assert not slot_grapple_eligible(actor, setup, conditional)
    target.state.is_dead = False
    assert slot_grapple_eligible(actor, setup, conditional)
