"""Source-first containment contract: all 327 cards and mutation negatives."""
from __future__ import annotations

import logging
import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_grapple_swallow_source_2014 import source_grapple_swallow_2014
from app.content.monster_sequence_engulf_source_2014 import source_sequence_containment_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.swallow_actions import swallow_action_from_source
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)
CORPUS = {monster.id: monster for monster in load_monster_source_2014()}


def test_all_327_source_grammars_find_one_two_hit_containment_family():
    try:
        assert len(CORPUS) == 327
        matches = {
            monster.id for monster in CORPUS.values()
            if source_sequence_containment_2014(monster) is not None
        }
        assert matches == {"shambling-mound"}
        card = CORPUS["shambling-mound"]
        snapshot = card.model_dump_json()
        proof = source_sequence_containment_2014(card)
        assert proof and proof.source_name == "Engulf"
        assert proof.attack_id == "slam"
        assert proof.required_sequence_hits == 2
        assert proof.max_target_size.value == "medium"
        assert proof.grapple_dc == 14
        assert (proof.damage_dice_count, proof.damage_dice_size, proof.damage_bonus) == (2, 8, 4)
        assert proof.damage_type == "bludgeoning"
        assert (proof.start_turn_save_ability, proof.start_turn_save_dc) == ("constitution", 14)
        assert card.model_dump_json() == snapshot
        assert basic_blockers_2014(card) == ()
    except Exception:
        logger.exception("2014 sequence containment source scan failed.")
        raise


def test_full_binding_compiles_real_multiattack_state_and_browser_template():
    try:
        card = CORPUS["shambling-mound"]
        profile = source_grapple_swallow_2014(card)
        assert profile and profile.delivery_mode == "attack_sequence"
        action = swallow_action_from_source(profile)
        assert action and action.required_sequence_hits == 2
        template = compile_combatant(adapt_basic_monster_2014(card))
        assert template.attack_action and len(template.attack_action.slots) == 2
        assert all(
            slot.attack_ids == ["2014-shambling-mound-slam"]
            for slot in template.attack_action.slots
        )
        assert len(template.swallow_actions) == 1
        assert template.swallow_actions[0].attack_id == "2014-shambling-mound-slam"
        assert template.swallow_actions[0].source_name == "Engulf"
        assert template.damage_absorptions[0].source_name == "Lightning Absorption"
        row = template_row(template)
        swallow = row["swallowActions"][0]
        assert swallow["deliveryMode"] == "attack_sequence"
        assert swallow["requiredSequenceHits"] == 2
        assert swallow["sequenceGrappleDc"] == 14
        assert swallow["startTurnSaveAbility"] == "constitution"
        assert swallow["startTurnSaveDc"] == 14
        assert swallow["damageBonus"] == 4
        assert swallow["cannotBreathe"] is True
        assert swallow["movesWithSource"] is True
        assert swallow["exitProne"] is False
        assert [slot["attackIds"] for slot in row["attack_action"]["slots"]] == [
            ["2014-shambling-mound-slam"], ["2014-shambling-mound-slam"],
        ]
    except Exception:
        logger.exception("2014 universal multiattack containment binding failed.")
        raise


@pytest.mark.parametrize("old,new", [
    ("two slam attacks", "one slam attack"),
    ("If both attacks hit", "If either attack hits"),
    ("Medium or smaller target", "Large or smaller target"),
    ("escape DC 14", "escape DC 15"),
    ("uses its Engulf on it", "uses its Slam on it"),
    ("unable to breathe", "able to breathe"),
    ("DC 14 Constitution saving throw", "DC 13 Constitution saving throw"),
    ("start of each of the mound's turns", "end of each of the mound's turns"),
    ("13 (2d8 + 4) bludgeoning damage", "13 (2d8 + 4) poison damage"),
    ("If the mound moves", "If the mound teleports"),
    ("one creature engulfed", "two creatures engulfed"),
])
def test_changed_printed_sequencing_or_state_never_admitted(old, new):
    try:
        card = CORPUS["shambling-mound"]
        mutated = card.model_copy(update={
            "source_actions": card.source_actions.replace(old, new),
        })
        assert mutated.source_actions != card.source_actions
        assert source_sequence_containment_2014(mutated) is None
    except Exception:
        logger.exception("Malformed printed same-target containment guard failed.")
        raise


def test_structured_card_mutations_and_renamed_ids_do_not_dispatch_by_name():
    try:
        card = CORPUS["shambling-mound"]
        baseline = source_sequence_containment_2014(card)
        assert baseline is not None
        renamed = card.model_copy(update={
            "id": "unrelated-cavern-beast", "name": "Cavern Guardian",
        })
        assert source_sequence_containment_2014(renamed) == baseline
        for key, value in (
            ("max_target_size", "large"),
            ("damage_bonus", 5),
            ("start_turn_save_dc", 15),
            ("requires_existing_grapple", False),
            ("exit_prone", True),
            ("source_death_release", "delayed"),
        ):
            corrupted = card.model_copy(update={
                "swallow_actions": [{**card.swallow_actions[0], key: value}],
            })
            assert source_sequence_containment_2014(corrupted) is None
    except Exception:
        logger.exception("Source identity/mutation neutrality contract failed.")
        raise
