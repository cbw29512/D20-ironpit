"""2014 regurgitating Swallow must be source-derived and fail closed."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_regurgitating_swallow_source_2014 import (
    source_proven_regurgitating_swallow_2014,
)


def test_exact_source_parameters_and_immutable_card():
    monsters = load_monster_source_2014()
    assert len(monsters) == 327
    monster = next(m for m in monsters if m.id == "behir")
    original = monster.model_dump_json()
    proof = source_proven_regurgitating_swallow_2014(monster)
    assert proof is not None
    assert proof.attack_id == "bite"
    assert proof.max_target_size == "medium"
    assert (proof.damage_dice_count, proof.damage_dice_size) == (6, 6)
    assert proof.damage_type == "acid"
    assert (proof.regurgitation_damage_threshold, proof.regurgitation_save_dc) == (30, 14)
    assert proof.regurgitation_save_ability == "constitution"
    assert (proof.regurgitation_range_ft, proof.exit_movement_ft) == (10, 15)
    assert monster.model_dump_json() == original


def test_changed_source_outcomes_are_rejected():
    monster = next(m for m in load_monster_source_2014() if m.id == "behir")
    for before, after in (
        ("30 damage or more", "20 damage or more"),
        ("DC 14 Constitution", "DC 13 Constitution"),
        ("one bite attack", "two bite attacks"),
        ("total cover", "half cover"),
        ("21 (6d6) acid", "21 (6d6) cold"),
        ("at the end of that turn", "at the start of that turn"),
        ("exiting prone", "exiting standing"),
    ):
        assert before in monster.source_actions
        changed = monster.model_copy(update={
            "source_actions": monster.source_actions.replace(before, after),
        })
        # Updated values are not silently reused from the original card.
        changed_proof = source_proven_regurgitating_swallow_2014(changed)
        assert changed_proof is None or changed_proof != source_proven_regurgitating_swallow_2014(monster)


def test_unrelated_simple_swallow_does_not_match():
    for monster in load_monster_source_2014():
        if monster.id in {"giant-frog", "giant-toad"}:
            assert source_proven_regurgitating_swallow_2014(monster) is None
