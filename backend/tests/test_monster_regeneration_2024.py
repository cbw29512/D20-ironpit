from __future__ import annotations

import pytest

from app.content.monster_catalog import load_monster_rows
from app.content.monster_regeneration_2024 import regeneration_trait_2024


def _traits(name: str) -> str:
    row = next(row for row in load_monster_rows() if row["name"] == name)
    return str(row["traits"])


@pytest.mark.parametrize(
    ("name", "amount", "positive_hp", "suppressed", "survives_zero"),
    [
        ("Oni", 10, True, set(), False),
        ("Shield Guardian", 10, True, set(), False),
        ("Troll", 15, False, {"acid", "fire"}, True),
        ("Troll Limb", 5, False, {"acid", "fire"}, True),
    ],
)
def test_printed_regeneration_compiles_to_universal_trait(
    name: str,
    amount: int,
    positive_hp: bool,
    suppressed: set[str],
    survives_zero: bool,
) -> None:
    trait = regeneration_trait_2024(_traits(name))
    assert trait is not None
    assert trait.amount == amount
    assert trait.requires_positive_hp is positive_hp
    assert {item.value for item in trait.suppressed_by_damage_types} == suppressed
    assert trait.survives_zero_until_turn is survives_zero


def test_no_regeneration_printed_means_no_runtime_trait() -> None:
    assert regeneration_trait_2024(_traits("Wolf")) is None


def test_unknown_regeneration_wording_fails_closed() -> None:
    with pytest.raises(ValueError):
        regeneration_trait_2024(
            "Regeneration. The creature mysteriously recovers whenever the moon is visible."
        )
