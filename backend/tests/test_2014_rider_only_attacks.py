from __future__ import annotations

import sys
from pathlib import Path

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monster_catalog_2014 import monster_by_id_2014

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


def test_guardian_naga_spit_poison_resolves_through_shared_attack_engine() -> None:
    naga = build_combatant_state(monster_by_id_2014("guardian-naga"))
    veteran = build_combatant_state(monster_by_id_2014("veteran"))
    attacks = (naga.template.weapon_attack, *naga.template.alternate_weapon_attacks)
    spit = next(attack for attack in attacks if attack.id == "spit-poison")
    hp_before = veteran.current_hp

    event = resolve_attack(
        1, 1, naga, veteran, spit, 15,
        FixedDiceProvider([9, 1, *([1] * 10)]),
        spend_action=False,
    )

    assert event.hit is True
    assert event.attack_roll is not None and event.attack_roll.total == 17
    assert event.save_ability == "constitution"
    assert event.save_dc == 15
    assert event.save_succeeded is False
    assert event.damage_roll is not None and event.damage_roll.total == 10
    assert event.hp_after == hp_before - 10
    assert len(event.damage_components) == 1
    assert event.damage_components[0].damage_type.value == "poison"
