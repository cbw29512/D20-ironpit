"""Universal 2014 source-card bridge for multi-target typed saving throw damage."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.content.capability_compiler import _compile_save
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.capability_effects import DiceSpec
from app.domain.save_damage import SaveDamageComponent
from app.domain.weapons import DamageType


def _synthetic_card(name: str) -> SaveCapabilityDefinition:
    return SaveCapabilityDefinition(
        id="custom-save", name=name, save_ability="dexterity", dc=16,
        range_ft=15, max_targets=4, success_damage="half",
        damage_components=[
            SaveDamageComponent(dice_count=3, dice_size=6, damage_bonus=4, damage_type="bludgeoning"),
            SaveDamageComponent(dice_count=3, dice_size=6, damage_bonus=4, damage_type="slashing"),
        ],
    )


@pytest.mark.parametrize("printed_name", ["Custom Impact", "Unrelated Homebrew Action"])
def test_typed_components_compile_without_name_dispatch(printed_name: str) -> None:
    compiled = _compile_save(_synthetic_card(printed_name))
    assert compiled.name == printed_name
    assert compiled.max_targets == 4
    assert compiled.damage_dice_count == 0
    assert compiled.damage_type is None
    assert compiled.success_damage == "half"
    assert [(item.dice_count, item.dice_size, item.damage_bonus, item.damage_type)
            for item in compiled.damage_components] == [
        (3, 6, 4, "bludgeoning"), (3, 6, 4, "slashing"),
    ]


def test_mixed_legacy_and_typed_damage_fails_closed() -> None:
    with pytest.raises(ValidationError, match="either legacy dice or typed components"):
        SaveCapabilityDefinition(
            id="invalid", name="Invalid", save_ability="dexterity", dc=16,
            range_ft=15, damage=DiceSpec(count=1, size=6),
            damage_type=DamageType.FIRE,
            damage_components=[SaveDamageComponent(
                dice_count=1, dice_size=6, damage_type="slashing",
            )],
        )


def test_legacy_save_damage_still_compiles() -> None:
    card = SaveCapabilityDefinition(
        id="legacy", name="Legacy", save_ability="constitution", dc=12,
        range_ft=30, damage=DiceSpec(count=2, size=6), damage_type=DamageType.FIRE,
    )
    action = _compile_save(card)
    assert action.damage_dice_count == 2
    assert action.damage_type == "fire"
    assert action.damage_components == []


def test_browser_card_serialization_preserves_multi_target_typed_components() -> None:
    """The production browser card must retain source target count and types."""
    import sys
    from pathlib import Path

    scripts = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from browser_template_serializer import _save

    row = _save(_compile_save(_synthetic_card("Renamed Source")))
    assert row["name"] == "Renamed Source"
    assert row["maxTargets"] == 4
    assert row["successDamage"] == "half"
    assert row["damageComponents"] == [
        {"diceCount": 3, "diceSize": 6, "damageBonus": 4, "damageType": "bludgeoning"},
        {"diceCount": 3, "diceSize": 6, "damageBonus": 4, "damageType": "slashing"},
    ]


def test_default_target_count_keeps_existing_browser_card_shape() -> None:
    import sys
    from pathlib import Path

    scripts = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from browser_template_serializer import _save

    legacy = SaveCapabilityDefinition(
        id="default-target", name="Default Target", save_ability="wisdom",
        dc=11, range_ft=30,
    )
    assert "maxTargets" not in _save(_compile_save(legacy))
