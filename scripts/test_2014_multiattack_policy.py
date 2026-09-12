from import_2014_multiattack import parse_multiattack


def attack(attack_id: str, name: str, kind: str = "melee") -> dict:
    return {"id": attack_id, "name": name, "kind": kind}


def main() -> int:
    grick = (
        "<p><strong>Multiattack.</strong> The grick makes one attack with its tentacles. "
        "If that attack hits, the grick can make one beak attack against the same target.</p>"
    )
    parsed = parse_multiattack(grick, [attack("tentacles", "Tentacles"), attack("beak", "Beak")])
    assert parsed == {
        "id": "multiattack", "name": "Multiattack", "slots": [["tentacles"], ["beak"]],
        "policy": {"requires_previous_hit_slots": [1], "same_target_as_previous_slots": [1]},
    }

    lizardfolk = (
        "<p><strong>Multiattack.</strong> The lizardfolk makes two melee attacks, "
        "each one with a different weapon.</p>"
    )
    parsed = parse_multiattack(lizardfolk, [
        attack("bite", "Bite"), attack("heavy-club", "Heavy Club"), attack("javelin", "Javelin", "ranged"),
    ])
    assert parsed["slots"] == [["bite", "heavy-club"], ["bite", "heavy-club"]]
    assert parsed["policy"] == {"distinct_attack_ids": True}

    fungus = "<p><strong>Multiattack.</strong> The fungus makes 1d4 Rotting Touch attacks.</p>"
    parsed = parse_multiattack(fungus, [attack("rotting-touch", "Rotting Touch")])
    assert parsed == {
        "id": "multiattack", "name": "Multiattack", "slots": [["rotting-touch"]],
        "policy": {"repeat_slot_index": 0, "repeat_dice_count": 1, "repeat_dice_size": 4},
    }

    purple_worm = (
        "<p><strong>Multiattack.</strong> The worm makes two attacks: one with its bite and one with its stinger.</p>"
    )
    parsed = parse_multiattack(purple_worm, [
        attack("bite", "Bite"), attack("tail-stinger", "Tail Stinger"),
    ])
    assert parsed == {
        "id": "multiattack", "name": "Multiattack", "slots": [["bite"], ["tail-stinger"]],
    }

    vampire_spawn = (
        "<p><strong>Multiattack.</strong> The vampire makes two attacks, only one of which can be a bite attack.</p>"
    )
    parsed = parse_multiattack(vampire_spawn, [attack("claws", "Claws"), attack("bite", "Bite")])
    assert parsed == {
        "id": "multiattack", "name": "Multiattack",
        "slots": [["claws", "bite"], ["claws", "bite"]],
        "policy": {"at_most_once_attack_ids": ["bite"]},
    }

    print("2014 Multiattack policy regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
