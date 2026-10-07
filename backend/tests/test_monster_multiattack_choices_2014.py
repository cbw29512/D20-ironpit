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
    "centaur": [["pike", "longbow"], ["hooves", "longbow"]],
    "merrow": [["bite"], ["claws", "harpoon", "harpoon-ranged"]],
    "sahuagin": [["bite"], ["claws", "spear", "spear-two-handed"]],
    "wight": [["life-drain", "longsword", "longsword-two-handed", "longbow"], ["longsword", "longsword-two-handed", "longbow"]],
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


@pytest.mark.parametrize("slots", [[[]], [["claws", "unbound"]]])
def test_malformed_slot_blocks_whole_monster_instead_of_dropping_an_option(slots):
    try:
        source = next(item for item in load_monster_source_2014() if item.id == "merrow")
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
        source = next(item for item in load_monster_source_2014() if item.id == "merrow")
        coupled = source.model_copy(update={"multiattack_policy": {"requires_same_kind": True}})
        assert "multiattack:complex" in basic_blockers_2014(coupled)
        with pytest.raises(ValueError, match="Unsupported Multiattack"):
            multiattack_2014(coupled)
    except Exception:
        logger.exception("Coupled source choice policy was incorrectly admitted.")
        raise



def test_merrow_ranged_harpoon_preserves_printed_pull_and_sahuagin_multiattack_is_melee_only():
    try:
        sources = {item.id: item for item in load_monster_source_2014()}
        runtime = compile_combatant(adapt_basic_monster_2014(sources["merrow"]))
        ranged = next(item for item in runtime.alternate_weapon_attacks if item.id.endswith("harpoon-ranged"))
        assert ranged.weapon.attack_kind.value == "ranged"
        assert ranged.weapon.normal_range_ft == 20
        assert ranged.weapon.long_range_ft == 60
        assert ranged.on_hit_contested_movement.distance_ft == 20
        sahuagin = sources["sahuagin"]
        by_id = {item.id: item for item in sahuagin.attacks}
        assert all(by_id[item].kind == "melee" for slot in sahuagin.multiattack_slots for item in slot)
        assert by_id["spear-ranged"].kind == "ranged"
    except Exception:
        logger.exception("Printed Harpoon or melee-only source restriction was lost.")
        raise
