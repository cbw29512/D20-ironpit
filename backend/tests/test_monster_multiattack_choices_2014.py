import logging

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_multiattack_2014 import multiattack_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)
# Independent printed-slot expectations: alternatives are choices, not extra strikes.
EXPECTED = {
    "bandit-captain": [["scimitar", "dagger-ranged"], ["scimitar", "dagger-ranged"], ["dagger-melee", "dagger-ranged"]],
    "centaur": [["pike", "longbow"], ["hooves", "longbow"]],
    "half-red-dragon-veteran": [["longsword", "longsword-two-handed"], ["longsword", "longsword-two-handed"], ["shortsword"]],
    "merrow": [["bite"], ["claws", "harpoon"]],
    "sahuagin": [["bite"], ["claws", "spear", "spear-ranged", "spear-two-handed"]],
    "veteran": [["longsword", "longsword-two-handed"], ["longsword", "longsword-two-handed"], ["shortsword"]],
    "wight": [["life-drain", "longbow"], ["longsword-two-handed", "longbow"]],
}


@pytest.mark.parametrize("source_id", EXPECTED)
def test_source_choice_slots_survive_compile_without_extra_strikes_or_attack_action_grants(source_id):
    try:
        source = next(item for item in load_monster_source_2014() if item.id == source_id)
        before = source.model_dump()
        assert basic_blockers_2014(source) == ()
        definition = adapt_basic_monster_2014(source)
        runtime = compile_combatant(definition)
        expected = [[f"2014-{source_id}-{item}" for item in slot] for slot in EXPECTED[source_id]]
        assert [slot.attack_ids for slot in definition.attack_action.slots] == expected
        assert [slot.attack_ids for slot in runtime.attack_action.slots] == expected
        assert definition.attack_action.is_attack_action is False
        assert runtime.attack_action.is_attack_action is False
        assert source.model_dump() == before
        assert runtime.ruleset == "2014"
    except Exception:
        logger.exception("2014 source Multiattack roundtrip failed for %s.", source_id)
        raise


@pytest.mark.parametrize("slots", [[[]], [["scimitar", "unbound"]]])
def test_malformed_slot_blocks_whole_monster_instead_of_dropping_an_option(slots):
    try:
        source = next(item for item in load_monster_source_2014() if item.id == "bandit-captain")
        invalid = source.model_copy(update={"multiattack_slots": slots})
        assert "multiattack:choice-or-binding" in basic_blockers_2014(invalid)
        with pytest.raises(ValueError, match="Unsupported Multiattack"):
            multiattack_2014(invalid)
        with pytest.raises(ValueError, match="not a basic 2014 candidate"):
            adapt_basic_monster_2014(invalid)
    except Exception:
        logger.exception("Malformed source Multiattack did not fail closed.")
        raise


def test_unmodeled_coupled_choice_policy_is_still_blocked():
    try:
        source = next(item for item in load_monster_source_2014() if item.id == "bandit-captain")
        coupled = source.model_copy(update={"multiattack_policy": {"requires_same_kind": True}})
        assert "multiattack:complex" in basic_blockers_2014(coupled)
        with pytest.raises(ValueError, match="Unsupported Multiattack"):
            multiattack_2014(coupled)
    except Exception:
        logger.exception("Coupled source choice policy was incorrectly admitted.")
        raise
