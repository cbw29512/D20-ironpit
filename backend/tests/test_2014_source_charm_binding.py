"""Source-verified 2014 Charm is a shared Save Action, not a named resolver."""
from __future__ import annotations

import logging

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_supported_extra_actions_2014 import source_supported_extra_action_labels_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_charm_control_2014 import source_proven_charm_control_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.capability_compiler import _compile_save
from scripts.browser_template_serializer import _save

logger = logging.getLogger(__name__)


def _card():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        matches = [x for x in cards if source_proven_charm_control_2014(x)]
        assert len(matches) == 1
        return matches[0]
    except Exception:
        logger.exception("2014 printed Charm source scan failed.")
        raise


def test_charm_compiles_to_source_named_universal_save_and_browser_fields():
    try:
        card = _card()
        before = card.model_dump_json()
        (definition,) = source_proven_charm_control_2014(card)
        runtime = _compile_save(definition)
        row = _save(runtime)
        assert definition.name == "Charm" == runtime.name == row["name"]
        assert runtime.save_ability == "wisdom" and runtime.dc == 15
        assert row["range"] == 30 and row["requiresTargetSight"]
        assert row["requiredTargetCreatureTypes"] == ["humanoid"]
        assert row["magicalEffect"]
        assert definition.effect_tags == ["charmed"]
        assert runtime.effect_tags == ["charmed"]
        assert row["effectTags"] == ["charmed"]
        assert row["sourceEffectImmunityOnSuccess"]
        rider = runtime.failed_save_timed_effect
        assert rider and rider.effect_id == "charmed"
        assert rider.duration_rounds == 14400
        assert rider.source_target_limit == 1
        assert rider.damage_repeat_save_trigger == "any_damage_source"
        assert rider.repeat_save_ability == "wisdom" and rider.repeat_save_dc == 15
        assert rider.repeat_save_timing is None
        assert rider.source_effect_immunity_on_end
        browser = row["failedSaveTimedEffect"]
        assert browser["damageRepeatSaveTrigger"] == "any_damage_source"
        assert browser["sourceTargetLimit"] == 1
        assert browser["repeatSaveTiming"] is None
        assert "Charm" in [x.name for x in save_capabilities_2014(card)]
        assert card.model_dump_json() == before
        # No scripted verbal/telepathic/suicidal commands in automated Pit:
        # the existing Charmed debuff is the full executable arena decision.
        assert "charm" in source_supported_extra_action_labels_2014(card)
        assert basic_blockers_2014(card) == ()
    except Exception:
        logger.exception("2014 source Charm definition, serializer or blocker failed.")
        raise


@pytest.mark.parametrize("old,new", [
    ("can see", "can hear"),
    ("30 feet", "90 feet"),
    ("DC 15 Wisdom", "DC 12 Wisdom"),
    ("1 day", "2 days"),
    ("obeys the fiend's verbal or telepathic commands", "ignores commands"),
    ("suffers any harm", "suffers cold damage"),
    ("suicidal command", "normal command"),
    ("next 24 hours", "next 12 hours"),
    ("only one target charmed at a time", "two targets charmed at a time"),
    ("effect on the previous target ends", "previous target stays charmed"),
])
def test_charm_source_mutations_fail_closed(old, new):
    try:
        card = _card()
        assert old in (card.source_actions or "")
        edited = card.model_copy(update={
            "source_actions": card.source_actions.replace(old, new),
        })
        assert not source_proven_charm_control_2014(edited)
        assert "charm" not in source_supported_extra_action_labels_2014(edited)
        assert "source:extra-action" in basic_blockers_2014(edited)
    except Exception:
        logger.exception("Charm source mutation failed for %s.", old)
        raise


def test_missing_heading_extra_unheaded_rider_and_renamed_identity():
    try:
        card = _card()
        renamed = card.model_copy(update={"id": "renamed-fiend", "name": "Other Name"})
        assert len(source_proven_charm_control_2014(renamed)) == 1
        altered = card.model_copy(update={
            "source_actions": card.source_actions.replace("<strong>Charm.</strong>",
                                                          "<strong>New Control.</strong>"),
        })
        assert not source_proven_charm_control_2014(altered)
        extra = card.model_copy(update={
            "source_actions": card.source_actions.replace(
                "<p><em><strong>Draining Kiss.",
                "<p>Additionally, the target is stunned.</p><p><em><strong>Draining Kiss.",
            ),
        })
        text = source_sections_2014(extra.source_actions, include_continuations=True)
        assert "Additionally" in text["Charm"]
        assert not source_proven_charm_control_2014(extra)
    except Exception:
        logger.exception("Charm source section completeness or identity test failed.")
        raise
