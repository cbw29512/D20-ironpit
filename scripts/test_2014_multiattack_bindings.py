from import_2014_multiattack import parse_multiattack


def attack(attack_id: str, name: str) -> dict:
    return {"id": attack_id, "name": name, "kind": "melee", "damage": {"average": 1}}


def binding(text: str, attacks: list[dict]) -> dict:
    parsed = parse_multiattack(f"<p><strong>Multiattack.</strong> {text}</p>", attacks)
    assert parsed is not None
    assert parsed["slots"] == []
    return parsed["binding"]


def main() -> int:
    grapple_extra = binding(
        "The creature makes two pincer attacks. If the creature is grappling a creature, "
        "the creature can also use its tentacles once.",
        [attack("pincer", "Pincer")],
    )
    assert grapple_extra == {
        "slots": [
            {"action_ids": ["pincer"]},
            {"action_ids": ["pincer"]},
            {"action_ids": ["tentacles"], "optional": True, "requirement": "source_has_grappled_target"},
        ]
    }

    available_extra = binding(
        "The creature makes one bite attack and, if it can, uses its Blinding Spittle.",
        [attack("bites", "Bites")],
    )
    assert available_extra == {
        "slots": [
            {"action_ids": ["bites"]},
            {"action_ids": ["blinding-spittle"], "optional": True, "requirement": "action_available"},
        ]
    }

    dynamic = binding(
        "The creature makes as many bite attacks as it has heads.",
        [attack("bite", "Bite")],
    )
    assert dynamic == {
        "slots": [{"action_ids": ["bite"]}],
        "repeat_slot_index": 0,
        "repeat_count_source": "heads",
    }

    replacement = binding(
        "The creature makes three tentacle attacks, each of which it can replace with one use of Fling.",
        [attack("tentacle", "Tentacle")],
    )
    assert replacement == {
        "slots": [
            {"action_ids": ["tentacle", "fling"]},
            {"action_ids": ["tentacle", "fling"]},
            {"action_ids": ["tentacle", "fling"]},
        ]
    }

    mixed_choice = binding(
        "The creature makes two attacks: one with its claws and one with its dagger or Intoxicating Touch.",
        [attack("claws", "Claws")],
    )
    assert mixed_choice == {
        "slots": [
            {"action_ids": ["claws"]},
            {"action_ids": ["dagger", "intoxicating-touch"]},
        ]
    }

    follow_up = binding(
        "The creature makes two slam attacks. If both attacks hit a Medium or smaller target, "
        "the target is grappled (escape DC 14), and the creature uses its Engulf on it.",
        [attack("slam", "Slam")],
    )
    assert follow_up == {
        "slots": [{"action_ids": ["slam"]}, {"action_ids": ["slam"]}],
        "follow_up_action_id": "engulf",
        "follow_up_condition": "all_attacks_hit_same_target",
        "follow_up_max_target_size": "medium",
        "follow_up_grapple_escape_dc": 14,
    }

    print("2014 generic Multiattack binding regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
