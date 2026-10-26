"""Fail-closed source mutations for the generic 2014 rechargeable self-buff binder."""
from __future__ import annotations

import pytest

from app.content.monster_recharge_self_buffs_2014 import (
    recharge_self_buff_bindings_2014,
)
from test_2014_clay_golem_haste import _source


@pytest.mark.parametrize("old,new", [
    ("Until the end of its next turn", "Until the end of its current turn"),
    ("has advantage on Dexterity saving throws", "has advantage on Strength saving throws"),
    ("can use its slam attack as a bonus action", "can use its fist attack as a bonus action"),
    ("magically gains", "gains"),
    ("Haste (Recharge 5–6)", "Haste (Recharge 4–6)"),
])
def test_changed_haste_semantics_fail_closed(old: str, new: str):
    try:
        source = _source()
        changed = source.model_copy(update={
            "source_actions": source.source_actions.replace(old, new),
        })
        assert recharge_self_buff_bindings_2014(changed) == []
    except Exception:
        raise


def test_valid_source_owned_ac_parameter_is_data_not_dispatch():
    try:
        source = _source()
        changed = source.model_copy(update={
            "id": "renamed-composite-buff-source",
            "name": "Unrelated Composite Source",
            "source_actions": source.source_actions.replace("+2 bonus", "+4 bonus"),
        })
        bindings = recharge_self_buff_bindings_2014(changed)
        assert len(bindings) == 1
        assert bindings[0].action.modifier_effects[0].flat_bonus == 4
        assert bindings[0].bonus_attack_grant.attack_ids == [
            "2014-renamed-composite-buff-source-slam"
        ]
    except Exception:
        raise


def test_recharge_action_display_name_is_not_dispatch_identity():
    try:
        source = _source()
        changed = source.model_copy(update={
            "source_actions": source.source_actions.replace(
                "Haste (Recharge 5–6)", "Overclock (Recharge 5–6)"
            ),
            "action_names": [
                "Overclock (Recharge 5–6)" if name == "Haste (Recharge 5–6)" else name
                for name in source.action_names
            ],
            "action_recharges": {"overclock": 5},
        })
        bindings = recharge_self_buff_bindings_2014(changed)
        assert len(bindings) == 1
        assert bindings[0].action.id == "overclock"
        assert bindings[0].action.name == "Overclock"
        assert bindings[0].recharge.resource_id == "overclock"
        assert bindings[0].bonus_attack_grant.required_active_effect_id == "overclock"
    except Exception:
        raise
