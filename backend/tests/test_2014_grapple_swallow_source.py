"""Two 2014 Swallow source cards prove one shared action grammar."""
from __future__ import annotations

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_grapple_swallow_source_2014 import source_grapple_swallow_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.size import CreatureSize


@pytest.fixture(scope="module")
def corpus():
    return {m.id: m for m in load_monster_source_2014()}


@pytest.mark.parametrize("monster_id,size,count,sides,exit_ft", [
    ("giant-frog", CreatureSize.SMALL, 2, 4, 5),
    ("giant-toad", CreatureSize.MEDIUM, 3, 6, 5),
])
def test_real_source_yields_complete_immutable_swallow_profile(
    corpus, monster_id, size, count, sides, exit_ft,
):
    monster = corpus[monster_id]
    original = monster.model_dump_json()
    profile = source_grapple_swallow_2014(monster)
    assert profile is not None
    assert profile.source_name == "Swallow"
    assert profile.attack_id == "bite"
    assert profile.max_target_size == size
    assert (profile.damage_dice_count, profile.damage_dice_size) == (count, sides)
    assert profile.damage_type == "acid"
    assert profile.max_swallowed == 1
    assert profile.exit_movement_ft == exit_ft
    assert "mechanic:swallow" not in basic_blockers_2014(monster)
    assert "source:extra-action" not in basic_blockers_2014(monster)
    assert monster.model_dump_json() == original


@pytest.mark.parametrize("replace_from,replace_to", [
    ("one bite attack", "two bite attacks"),
    ("If the attack hits", "If the attack misses"),
    ("the grapple ends", "the grapple continues"),
    ("blinded and restrained", "blinded but not restrained"),
    ("total cover", "half cover"),
    ("acid damage", "poison damage"),
    ("only one target swallowed", "two targets swallowed"),
    ("using 5 feet of movement", "using 10 feet of movement"),
    ("exiting prone", "exiting standing"),
])
def test_changed_or_extra_effect_never_admitted(corpus, replace_from, replace_to):
    monster = corpus["giant-frog"]
    assert replace_from in monster.source_actions
    changed = monster.model_copy(update={
        "source_actions": monster.source_actions.replace(
            replace_from, replace_to,
        ),
    })
    assert source_grapple_swallow_2014(changed) is None
    assert "mechanic:swallow" in basic_blockers_2014(changed)


def test_inconsistent_structured_damage_or_size_fails_closed(corpus):
    monster = corpus["giant-toad"]
    for field, value in (
        ("damage_dice_size", 8), ("max_target_size", "small"),
        ("max_swallowed", 2), ("requires_existing_grapple", False),
    ):
        altered = monster.model_copy(update={
            "swallow_actions": [{**monster.swallow_actions[0], field: value}],
        })
        assert source_grapple_swallow_2014(altered) is None


def test_different_swallow_grammars_remain_separately_blocked(corpus):
    for monster_id in ("purple-worm", "shambling-mound"):
        assert source_grapple_swallow_2014(corpus[monster_id]) is None
        assert "mechanic:swallow" in basic_blockers_2014(corpus[monster_id])



@pytest.mark.parametrize(
    "monster_id,threshold,dc,range_ft,all_swallowed,delivery_mode",
    [
        ("behir", 30, 14, 10, False, "action_attack"),
        ("remorhaz", 30, 15, 10, True, "action_attack"),
        ("kraken", 50, 25, 10, True, "attack_hit"),
        ("tarrasque", 60, 20, 10, True, "action_attack"),
    ],
)
def test_threshold_regurgitation_profiles_are_source_proven(
    corpus, monster_id, threshold, dc, range_ft, all_swallowed, delivery_mode,
):
    monster = corpus[monster_id]
    original = monster.model_dump_json()
    profile = source_grapple_swallow_2014(monster)

    assert profile is not None
    assert profile.source_name == "Swallow"
    assert profile.attack_id == "bite"
    assert profile.delivery_mode == delivery_mode
    assert profile.regurgitation_damage_threshold == threshold
    assert profile.regurgitation_save_ability == "constitution"
    assert profile.regurgitation_save_dc == dc
    assert profile.regurgitation_range_ft == range_ft
    assert profile.regurgitation_all_swallowed is all_swallowed
    assert monster.model_dump_json() == original


def test_source_identity_is_not_the_dispatch_key(corpus):
    monster = corpus["giant-frog"]
    renamed = monster.model_copy(update={
        "id": "cavern-frog", "name": "Cavern Frog",
    })
    assert source_grapple_swallow_2014(renamed) == source_grapple_swallow_2014(monster)


def test_shared_action_schema_and_browser_card_preserve_printed_parameters(corpus):
    from app.content.demo import build_demo_fighter
    from app.domain.swallow_actions import swallow_action_from_source
    from scripts.browser_template_serializer import template_row

    for monster_id, size, count, sides in (
        ("giant-frog", "small", 2, 4),
        ("giant-toad", "medium", 3, 6),
    ):
        profile = source_grapple_swallow_2014(corpus[monster_id])
        action = swallow_action_from_source(profile)
        assert action is not None
        assert action.requires_existing_grapple is True
        assert action.max_target_size.value == size
        card = build_demo_fighter().model_copy(update={"swallow_actions": [action]})
        row = template_row(card)
        serialized = row["swallowActions"][0]
        assert serialized["sourceName"] == "Swallow"
        assert serialized["attackId"] == "bite"
        assert serialized["maxTargetSize"] == size
        assert serialized["damageDiceCount"] == count
        assert serialized["damageDiceSize"] == sides
        assert serialized["damageType"] == "acid"
        assert serialized["grantsTotalExternalCover"] is True
        assert serialized["blindsAndRestrains"] is True
        assert serialized["maxSwallowed"] == 1
        assert basic_blockers_2014(corpus[monster_id]) == ()



def test_kraken_browser_card_uses_attack_hit_delivery(corpus):
    from app.content.demo import build_demo_fighter
    from app.domain.swallow_actions import swallow_action_from_source
    from scripts.browser_template_serializer import template_row

    profile = source_grapple_swallow_2014(corpus["kraken"])
    action = swallow_action_from_source(profile)
    assert action is not None
    assert action.delivery_mode == "attack_hit"
    row = template_row(build_demo_fighter().model_copy(update={"swallow_actions": [action]}))
    serialized = row["swallowActions"][0]
    assert serialized["deliveryMode"] == "attack_hit"


def test_complete_327_card_source_scan_has_no_unproven_swallow_bindings(corpus):
    assert len(corpus) == 327
    proven = {
        monster.id for monster in corpus.values()
        if source_grapple_swallow_2014(monster) is not None
    }
    assert proven == {"behir", "giant-frog", "giant-toad", "kraken", "remorhaz", "tarrasque"}
    for monster_id in proven:
        blockers = basic_blockers_2014(corpus[monster_id])
        assert "mechanic:swallow" not in blockers
        assert "source:extra-action" not in blockers
    for monster_id in ("behir", "giant-frog", "giant-toad", "remorhaz"):
        assert basic_blockers_2014(corpus[monster_id]) == ()


def test_admitted_runtime_and_browser_reference_the_compiled_bite_id(corpus):
    from app.content.capability_compiler import compile_combatant
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from scripts.browser_template_serializer import template_row

    for monster_id in ("giant-frog", "giant-toad"):
        expected = f"2014-{monster_id}-bite"
        runtime = compile_combatant(adapt_basic_monster_2014(corpus[monster_id]))
        assert runtime.weapon_attack.id == expected
        assert runtime.swallow_actions[0].attack_id == expected
        assert template_row(runtime)["swallowActions"][0]["attackId"] == expected
