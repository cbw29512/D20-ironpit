"""Source-proof regressions for on-hit start-turn timed condition damage."""
from __future__ import annotations

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_start_turn_damage_condition_2014 import (
    source_proven_start_turn_damage_condition_2014,
)


def _source():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "pit-fiend")
    except Exception as exc:
        raise AssertionError("Pinned 2014 Pit Fiend source is missing.") from exc


def _bite(monster):
    try:
        return next(attack for attack in monster.attacks if attack.id == "bite")
    except Exception as exc:
        raise AssertionError("Pinned Pit Fiend Bite source is missing.") from exc


def test_exact_source_proves_generic_start_turn_damage_condition_parameters():
    monster = _source()
    attack = _bite(monster)
    snapshot = monster.model_dump_json()

    proof = source_proven_start_turn_damage_condition_2014(monster, attack)

    assert proof is not None
    assert proof.condition_id == "poisoned"
    assert proof.save_ability == "constitution"
    assert proof.dc == 21
    assert proof.cannot_regain_hit_points is True
    assert (
        proof.start_of_turn_damage_dice_count,
        proof.start_of_turn_damage_dice_size,
        proof.start_of_turn_damage_type,
    ) == (6, 6, "poison")
    assert proof.repeat_save_timing == "target_turn_end"
    assert monster.model_dump_json() == snapshot


def test_monster_identity_is_not_a_source_proof_dispatch_key():
    monster = _source().model_copy(update={
        "id": "renamed-fiend-source",
        "name": "Renamed Fiend Source",
    })

    proof = source_proven_start_turn_damage_condition_2014(monster, _bite(monster))

    assert proof is not None
    assert proof.dc == 21
    assert proof.start_of_turn_damage_type == "poison"


def test_changed_timing_or_damage_text_fails_closed():
    monster = _source()
    bite = _bite(monster)
    for old, new in (
        ("at the start of each of its turns", "at the end of each of its turns"),
        ("21 (6d6) poison damage", "14 (4d6) poison damage"),
        ("DC 21 Constitution saving throw", "DC 20 Constitution saving throw"),
    ):
        changed = monster.model_copy(update={
            "source_actions": monster.source_actions.replace(old, new),
        })
        assert source_proven_start_turn_damage_condition_2014(changed, bite) is None


def test_preexisting_unreviewed_attack_rider_fails_closed():
    monster = _source()
    bite = _bite(monster).model_copy(update={
        "on_hit_damage": [{
            "average": 1,
            "dice_count": 1,
            "dice_size": 2,
            "bonus": 0,
            "type": "fire",
        }],
    })

    assert source_proven_start_turn_damage_condition_2014(monster, bite) is None
