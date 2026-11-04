"""Generic attachment-state tests; 2014 direct HP loss is not typed damage."""
import pytest

from app.combat.attachments import (
    Attachment, active_attachment_target, attach, detach_for_combatant,
    linked_attachment_effects, record_attachment_hp_loss, detach_link,
)


def _link(source="source-1", target="target-1", effect="feeding"):
    # The attack's initial Piercing hit is resolved separately by the attack engine.
    return Attachment(
        source, target, effect, 1, 4, None,
        periodic_effect_kind="direct_hp_loss", source_name="Blood Drain", damage_bonus=3,
        detach_after_hp_lost=10,
    )


def test_source_owned_direct_hp_loss_does_not_become_piercing_damage():
    row = _link()
    assert row.periodic_effect_kind == "direct_hp_loss"
    assert row.damage_type is None
    assert (row.damage_dice_count, row.damage_dice_size, row.damage_bonus) == (1, 4, 3)
    assert row.damage_timing == "source_turn_start"
    assert row.actual_hp_lost == 0


def test_attachment_has_no_grapple_or_speed_semantics():
    link = _link()
    assert attach((), link) == (link,)
    assert not hasattr(link, "grappled")
    assert not hasattr(link, "speed_penalty")


def test_cleanup_removes_both_linked_statuses_on_either_death():
    linked = attach((), _link())
    assert detach_for_combatant(linked, "source-1") == ()
    assert detach_for_combatant(linked, "target-1") == ()
    assert linked_attachment_effects(detach_for_combatant(linked, "target-1")) == ()


def test_actual_hp_loss_detaches_after_ten_not_after_initial_hit():
    linked = attach((), _link())
    # Only post-attachment recurrent HP loss is recorded here.
    linked = record_attachment_hp_loss(linked, "source-1", "feeding", 4)
    assert linked[0].actual_hp_lost == 4
    assert record_attachment_hp_loss(linked, "source-1", "feeding", 6) == ()


def test_zero_effective_hp_loss_does_not_advance_drain():
    linked = attach((), _link())
    assert record_attachment_hp_loss(linked, "source-1", "feeding", 0) == linked
    with pytest.raises(ValueError):
        record_attachment_hp_loss(linked, "source-1", "feeding", -1)


def test_duplicate_source_effect_fails_closed():
    with pytest.raises(ValueError):
        attach(attach((), _link()), _link(target="another-target"))


def test_attachment_projects_target_debuff_source_buff_without_healing():
    linked = attach((), _link())
    assert [(e.owner_id, e.counterpart_id, e.effect_id, e.kind)
            for e in linked_attachment_effects(linked)] == [
        ("target-1", "source-1", "attached", "debuff"),
        ("source-1", "target-1", "feeding", "buff"),
    ]
    assert active_attachment_target(linked, "source-1", "feeding") == "target-1"


def test_typed_damage_variant_is_same_generic_link_not_a_new_resolver():
    row = Attachment(
        "another-source", "another-target", "drain", 2, 4, "necrotic",
        periodic_effect_kind="typed_damage", source_name="Synthetic Drain",
    )
    assert row.periodic_effect_kind == "typed_damage"
    assert row.damage_type == "necrotic"
    assert row.damage_bonus == 0
    assert active_attachment_target(attach((), row), row.source_id, row.effect_id) == row.target_id


def test_malformed_periodic_effect_fails_closed():
    with pytest.raises(ValueError):
        Attachment("source", "target", "effect", 1, 4, "piercing",
                   periodic_effect_kind="direct_hp_loss", source_name="Invalid")
    with pytest.raises(ValueError):
        Attachment("source", "target", "effect", 1, 4, None,
                   periodic_effect_kind="typed_damage", source_name="Invalid")
    with pytest.raises(ValueError):
        Attachment("source", "target", "effect", 1, 4, None,
                   periodic_effect_kind="unknown", source_name="Invalid")


def test_identity_relabeling_does_not_change_link_behavior():
    a = attach((), _link(source="monster", target="hero", effect="bite"))
    b = attach((), _link(source="homebrew", target="other", effect="needle"))
    assert record_attachment_hp_loss(a, "monster", "bite", 10) == ()
    assert record_attachment_hp_loss(b, "homebrew", "needle", 10) == ()

def test_detach_link_only_removes_exact_owner_and_effect():
    first = _link(source="one", target="a", effect="feed")
    second = _link(source="two", target="b", effect="feed")
    third = _link(source="one", target="c", effect="other")
    linked = (first, second, third)
    assert detach_link(linked, "one", "feed") == (second, third)
    assert detach_link(linked, "absent", "feed") == linked
