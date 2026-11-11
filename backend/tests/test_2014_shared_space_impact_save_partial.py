"""Cross-roster source proof for partially bound shared-space impact saves."""
from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_save_capabilities_2014 import (
    recharge_rules_2014, save_resources_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_shared_space_impact_save_2014 import (
    source_proven_shared_space_impact_saves_2014,
)
from scripts.browser_template_serializer import template_row


def _cards():
    rows = load_monster_source_2014()
    assert len(rows) == 327
    return {card.id: card for card in rows}


def test_327_cards_find_only_printed_shared_space_impact_family():
    cards = _cards()
    found = {
        key: saves for key, card in cards.items()
        if (saves := source_proven_shared_space_impact_saves_2014(card))
    }
    assert set(found) == {"air-elemental"}
    (action,) = found["air-elemental"]
    assert (action.id, action.name, action.dc, action.save_ability) == (
        "whirlwind", "Whirlwind", 13, "strength",
    )
    assert (action.damage.count, action.damage.size, action.damage.bonus) == (3, 8, 2)
    assert action.damage_type.value == "bludgeoning"
    assert action.success_damage == "half"
    assert action.area.shape == "shared-space" and action.area.origin == "self"
    assert action.max_targets == 20 and action.target_scope == "all-other-creatures"
    assert action.failed_save_timed_effect.effect_id == "prone"
    assert action.failed_save_timed_effect.expiry_timing is None
    # Random fling/collision mechanics are not represented as a false
    # straight-line push that would move the target or ignore extra damage.
    assert action.failed_save_push_ft == 0
    assert action.resource_id == "whirlwind"


def test_source_compiler_recharge_browser_and_remaining_blocker():
    card = _cards()["air-elemental"]
    before = card.model_dump_json()
    template = compile_combatant(adapt_monster_mechanics_2014(card))
    (action,) = [save for save in template.saving_throw_actions if save.id == "whirlwind"]
    assert action.dc == 13
    assert (action.damage_dice_count, action.damage_dice_size, action.damage_bonus) == (
        3, 8, 2,
    )
    assert action.success_damage == "half"
    assert action.failed_save_timed_effect.effect_id == "prone"
    assert action.failed_save_timed_effect.expiry_timing is None
    assert [r.minimum_roll for r in recharge_rules_2014(card) if r.resource_id == "whirlwind"] == [4]
    assert [r.max_uses for r in save_resources_2014(card) if r.id == "whirlwind"] == [1]
    (browser,) = [
        row for row in template_row(template)["saving_throw_actions"]
        if row["id"] == "whirlwind"
    ]
    assert browser["damageBonus"] == 2
    assert browser["successDamage"] == "half"
    assert browser["failedSaveTimedEffect"]["effectId"] == "prone"
    assert browser["failedSaveTimedEffect"]["expiryTiming"] is None
    assert "mechanic:recharge" not in basic_blockers_2014(card)
    # Every combat-effective rider is already compiled. The only omitted
    # clauses require displacement/collision, impossible in this locked Pit.
    assert basic_blockers_2014(card) == ()
    assert before == card.model_dump_json()


def test_unknown_collision_rider_fails_closed_but_rename_reuses_primitive():
    card = _cards()["air-elemental"]
    for old, new in (
        ("3d8 + 2", "3d8 + 3"),
        ("for every 10 feet it was thrown", "for every 10 feet and blinds it"),
        ("in a random direction and knocked prone", "in a random direction and stunned"),
        ("Dexterity saving throw", "Constitution saving throw"),
    ):
        assert old in card.source_actions
        changed = card.model_copy(update={
            "source_actions": card.source_actions.replace(old, new),
        })
        assert source_proven_shared_space_impact_saves_2014(changed) == []
        assert "source:extra-action" in basic_blockers_2014(changed)
    renamed = card.model_copy(update={
        "id": "synthetic-air-source",
        "name": "Synthetic Air Source",
        "source_actions": card.source_actions.replace(
            "Whirlwind (Recharge 4–6)", "Squall (Recharge 4–6)",
        ),
        "action_names": [
            name.replace("Whirlwind (Recharge 4–6)", "Squall (Recharge 4–6)")
            for name in card.action_names
        ],
        "action_recharges": {"squall": 4},
    })
    (action,) = source_proven_shared_space_impact_saves_2014(renamed)
    assert (action.id, action.name) == ("squall", "Squall")
    assert action.damage.model_dump() == (
        source_proven_shared_space_impact_saves_2014(card)[0].damage.model_dump()
    )
