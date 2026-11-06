"""2014 held-target poison family: strict source → universal save + sequence."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_grappled_poison_2014 import (
    source_proven_grappled_poison_saves_2014,
)
from app.content.monster_grapple_followup_multiattack_2014 import (
    source_proves_grapple_followup_multiattack_2014,
)
from app.content.monster_multiattack_2014 import multiattack_blockers_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.capability_compiler import compile_combatant

logger = logging.getLogger(__name__)


def _card():
    try:
        return next(m for m in load_monster_source_2014() if m.id == "chuul")
    except Exception:
        logger.exception("Pinned source Chuul missing")
        raise


def test_roster_and_source_owned_poison_save_are_complete():
    try:
        roster = load_monster_source_2014()
        matched = [
            (source.id, action)
            for source in roster
            for action in source_proven_grappled_poison_saves_2014(source)
        ]
        assert len(roster) == 327 and len(matched) == 1
        assert matched[0][0] == "chuul"
        action = matched[0][1]
        assert (action.id, action.name, action.dc, action.range_ft) == (
            "tentacles", "Tentacles", 13, 10,
        )
        assert action.requires_target_grappled_by_source
        rider = action.failed_save_timed_effect
        assert rider.effect_id == "poisoned"
        assert rider.additional_effect_ids == ["paralyzed"]
        assert rider.duration_rounds == 10
        assert (rider.repeat_save_ability, rider.repeat_save_dc,
                rider.repeat_save_timing) == ("constitution", 13, "target_turn_end")
        card = _card()
        snapshot = card.model_dump_json()
        assert source_proves_grapple_followup_multiattack_2014(card, {"tentacles"})
        assert multiattack_blockers_2014(card) == []
        assert basic_blockers_2014(card) == ()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        assert template.attack_action is not None
        assert [slot.attack_ids for slot in template.attack_action.slots] == [
            ["2014-chuul-pincer"], ["2014-chuul-pincer"], [],
        ]
        assert template.attack_action.slots[2].save_action_ids == ["tentacles"]
        assert template.attack_action.slots[2].requires_source_grapple
        assert any(a.id == "tentacles" for a in template.saving_throw_actions)
        assert len([a for a in save_capabilities_2014(card) if a.name == "Tentacles"]) == 1
        assert card.model_dump_json() == snapshot
    except Exception:
        logger.exception("2014 held-target poison source/compilation failed")
        raise


def test_source_mutations_and_renamed_creature_fail_closed_or_preserve_mechanics():
    try:
        card = _card()
        for original, altered in (
            ("DC 13 Constitution", "DC 16 Wisdom"),
            ("for 1 minute", "for 2 hours"),
            ("Until this poison ends", "After the grapple ends"),
            ("repeat the saving throw at the end", "repeat the saving throw at the start"),
            ("on a success.", "on a success. The target also takes 1d8 acid damage."),
        ):
            assert original in card.source_actions
            changed = card.model_copy(update={
                "source_actions": card.source_actions.replace(original, altered),
            })
            assert not source_proven_grappled_poison_saves_2014(changed)
            assert "source:extra-action" in basic_blockers_2014(changed)
        for original, altered in (
            ("two pincer attacks", "three pincer attacks"),
            ("can also use its tentacles once", "can also use its tentacles twice"),
            ("is grappling a creature", "can see a creature"),
        ):
            changed = card.model_copy(update={
                "source_actions": card.source_actions.replace(original, altered),
            })
            assert multiattack_blockers_2014(changed) == ["multiattack:complex"]
        named = card.model_copy(update={
            "id": "renamed-holding-source",
            "name": "Holding Source",
            "source_actions": card.source_actions.replace("chuul", "holding source"),
        })
        assert source_proven_grappled_poison_saves_2014(named)[0].dc == 13
        assert not multiattack_blockers_2014(named)
    except Exception:
        logger.exception("2014 held-target poison fail-closed source tests failed")
        raise
