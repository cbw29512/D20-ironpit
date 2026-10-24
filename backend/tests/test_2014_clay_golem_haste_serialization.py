"""Browser serialization parity for 2014 Clay Golem Haste composition."""
from __future__ import annotations

from scripts.browser_template_serializer import template_row

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from test_2014_clay_golem_haste import _source


def test_clay_haste_serializes_active_effect_gate_and_recharge():
    try:
        template = compile_combatant(adapt_basic_monster_2014(_source()))
        row = template_row(template)
        haste = next(
            item for item in row["timed_self_buff_actions"] if item["id"] == "haste"
        )
        grant = next(
            item for item in row["bonusAttackGrants"] if item["name"] == "Haste"
        )
        recharge = next(
            item for item in row["recharge_rules"] if item["resourceId"] == "haste"
        )

        assert haste["actionCost"] == "action"
        assert haste["durationRounds"] == 1
        assert haste["expiryTiming"] == "source_turn_end"
        assert haste["magicalEffect"] is True
        assert haste["modifierEffects"] == [{
            "kind": "armor-class",
            "flatBonus": 2,
        }]
        assert haste["savingThrowAdvantageGrants"][0]["abilities"] == ["dexterity"]
        assert grant["requiredActiveEffectId"] == "haste"
        assert grant["attackIds"] == ["2014-clay-golem-slam"]
        assert grant["attackCount"] == 1
        assert recharge == {
            "resourceId": "haste",
            "minimumRoll": 5,
            "dieSize": 6,
        }
    except Exception:
        raise
