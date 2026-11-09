"""2014 Whelm source components bind without falsely admitting incomplete Action."""
from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_save_capabilities_2014 import (
    recharge_rules_2014,
    save_resources_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_shared_space_held_save_2014 import (
    source_proven_shared_space_held_saves_2014,
)
from app.domain.size import CreatureSize
from scripts.browser_template_serializer import template_row


def _cards():
    rows = load_monster_source_2014()
    assert len(rows) == 327
    return {row.id: row for row in rows}


def test_full_roster_has_exactly_one_source_verified_action():
    cards = _cards()
    found = {
        key: actions
        for key, card in cards.items()
        if (actions := source_proven_shared_space_held_saves_2014(card))
    }
    assert list(found) == ["water-elemental"]
    (action,) = found["water-elemental"]
    assert (action.id, action.name, action.dc, action.save_ability) == (
        "whelm", "Whelm", 15, "strength",
    )
    assert (action.damage.count, action.damage.size, action.damage.bonus) == (2, 8, 4)
    assert action.damage_type.value == "bludgeoning"
    assert action.success_damage == "none"  # Printed save success does not take damage.
    assert action.area.shape == "shared-space"
    assert action.area.origin == "self"
    assert action.target_scope == "all-other-creatures"
    assert action.max_targets == 20
    assert action.grapple.escape_dc == 14
    assert action.grapple.max_target_size == CreatureSize.LARGE
    assert action.grapple.size_only_applies_to_grapple
    assert action.grapple.max_active_grapples == 2
    assert action.grapple.large_target_slot_cost == 2
    assert action.grapple.restrains
    assert action.grapple.prevents_breathing
    assert action.resource_id == "whelm"


def test_compiler_recharge_and_browser_carry_source_parameters_but_stay_blocked():
    card = _cards()["water-elemental"]
    original = card.model_dump_json()
    template = compile_combatant(adapt_monster_mechanics_2014(card))
    (save,) = [a for a in template.saving_throw_actions if a.id == "whelm"]
    assert save.dc == 15 and save.damage_bonus == 4
    assert save.grapple_max_active_grapples == 2
    assert save.grapple_max_target_size == CreatureSize.LARGE
    assert save.grapple_prevents_breathing
    assert [r.minimum_roll for r in recharge_rules_2014(card) if r.resource_id == "whelm"] == [4]
    assert [r.max_uses for r in save_resources_2014(card) if r.id == "whelm"] == [1]
    browser = template_row(template)
    (payload,) = [a for a in browser["saving_throw_actions"] if a["id"] == "whelm"]
    assert payload["damageBonus"] == 4
    assert payload["grappleMaxActiveGrapples"] == 2
    assert payload["grappleMaxTargetSize"] == "large"
    assert payload["grappleLargeTargetSlotCost"] == 2
    assert "source:extra-action" in basic_blockers_2014(card)
    assert "mechanic:recharge" not in basic_blockers_2014(card)
    assert card.model_dump_json() == original


def test_full_source_mutations_fail_closed_and_rename_does_not_affect_resolution():
    card = _cards()["water-elemental"]
    for old, new in (
        ("2d8 + 4", "2d8 + 5"),
        ("unless it can breathe water", "unless it can breathe air"),
        ("one Large creature or up to two Medium", "two Large creatures or up to two Medium"),
        ("escape DC 14", "escape DC 15"),
        # An unknown rescue restriction is not part of the printed grammar.
        ("A creature within 5 feet", "A creature within 5 feet that is blinded"),
    ):
        assert old in card.source_actions
        changed = card.model_copy(update={
            "source_actions": card.source_actions.replace(old, new),
        })
        assert source_proven_shared_space_held_saves_2014(changed) == []
    # The helper's distance is an independently parameterized, still-unbound
    # rider. Changing a valid printed number must not invalidate the already
    # supported save/recharge component, nor falsely admit the monster.
    ranged_helper = card.model_copy(update={
        "source_actions": card.source_actions.replace(
            "A creature within 5 feet", "A creature within 10 feet",
        ),
    })
    (baseline,) = source_proven_shared_space_held_saves_2014(card)
    (same_save,) = source_proven_shared_space_held_saves_2014(ranged_helper)
    assert same_save.model_dump() == baseline.model_dump()
    assert "source:extra-action" in basic_blockers_2014(ranged_helper)

    renamed = card.model_copy(update={
        "id": "generic-fluid-source",
        "name": "Generic Fluid Source",
        "source_actions": card.source_actions.replace(
            "Whelm (Recharge 4–6)", "Torrent (Recharge 4–6)",
        ),
        "action_names": [
            name.replace("Whelm (Recharge 4–6)", "Torrent (Recharge 4–6)")
            for name in card.action_names
        ],
        "action_recharges": {"torrent": 4},
    })
    (renamed_action,) = source_proven_shared_space_held_saves_2014(renamed)
    assert (renamed_action.id, renamed_action.name) == ("torrent", "Torrent")
    assert renamed_action.damage.model_dump() == (
        source_proven_shared_space_held_saves_2014(card)[0].damage.model_dump()
    )
