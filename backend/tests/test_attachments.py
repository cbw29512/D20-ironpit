"""Reusable attachment state must not introduce Grappled semantics."""
import pytest
from app.combat.attachments import Attachment, attach, detach_for_combatant, record_attachment_damage


def _link():
    return Attachment("stirge-1", "hero-1", "blood-drain", 1, 4, "piercing", detach_damage_total=10)


def test_attaches_without_adding_a_grapple_condition():
    link = _link()
    assert attach((), link) == (link,)
    assert not hasattr(link, "grappled")


def test_detaches_when_source_or_target_leaves_combat():
    linked = attach((), _link())
    assert detach_for_combatant(linked, "stirge-1") == ()
    assert detach_for_combatant(linked, "hero-1") == ()


def test_damage_accumulates_and_detaches_at_configured_threshold():
    linked = attach((), _link())
    linked = record_attachment_damage(linked, "stirge-1", "blood-drain", 4)
    assert linked[0].accumulated_damage == 4
    assert record_attachment_damage(linked, "stirge-1", "blood-drain", 6) == ()


def test_duplicate_source_attachment_fails_closed():
    with pytest.raises(ValueError):
        attach(attach((), _link()), _link())
