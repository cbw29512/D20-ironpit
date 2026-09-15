from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from import_2014_monster_catalog import _attack  # noqa: E402


def test_spit_poison_parses_as_zero_direct_damage_attack_with_save_rider() -> None:
    paragraph = (
        "<p><em><strong>Spit Poison.</strong></em> Ranged Weapon Attack: +8 to hit, "
        "range 15/30 ft., one creature. Hit: The target must make a DC 15 Constitution "
        "saving throw, taking 45 (10d8) poison damage on a failed save, or half as much "
        "damage on a successful one.</p>"
    )

    attack = _attack(paragraph)

    assert attack is not None
    assert attack["id"] == "spit-poison"
    assert attack["kind"] == "ranged"
    assert attack["attack_bonus"] == 8
    assert attack["normal_range_ft"] == 15
    assert attack["long_range_ft"] == 30
    assert attack["damage"] == {
        "average": 0, "dice_count": 0, "dice_size": 6, "bonus": 0, "type": None,
    }
    assert attack["on_hit_save_effect"] == {
        "save_ability": "constitution",
        "dc": 15,
        "damage_dice_count": 10,
        "damage_dice_size": 8,
        "damage_bonus": 0,
        "damage_type": "poison",
        "success_damage": "half",
    }
    assert attack["source_complete"] is True
    assert attack["unsupported_text"] is None


def test_rider_only_parser_does_not_accept_unmodeled_hit_text() -> None:
    paragraph = (
        "<p><em><strong>Mystery Ray.</strong></em> Ranged Weapon Attack: +5 to hit, "
        "range 30/60 ft., one creature. Hit: Something unmodeled happens.</p>"
    )

    assert _attack(paragraph) is None
