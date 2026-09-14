from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from app.content.weapon_catalog_2014 import select_damage_mode_2014


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
IMPORTER = SCRIPTS / "import_2014_monster_catalog.py"


def _load_importer():
    # The importer intentionally uses sibling script imports, so expose the
    # scripts directory while loading it exactly as the CLI does.
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location("import_2014_monster_catalog_test", IMPORTER)
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load the 2014 monster importer.")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


@pytest.mark.parametrize("wording", ("if used", "when used", "if wielded", "when wielded"))
def test_versatile_attack_wording_compiles_to_two_damage_modes(wording: str) -> None:
    importer = _load_importer()
    paragraph = (
        "<strong>Quarterstaff.</strong> Melee Weapon Attack: +2 to hit, reach 5 ft., one target. "
        f"Hit: 3 (1d6) bludgeoning damage, or 4 (1d8) bludgeoning damage {wording} with two hands."
    )

    attacks = importer._attacks(paragraph)

    assert [attack["id"] for attack in attacks] == ["quarterstaff", "quarterstaff-two-handed"]
    assert all(attack["source_complete"] for attack in attacks)
    assert attacks[0]["damage"]["dice_size"] == 6
    assert attacks[1]["damage"]["dice_size"] == 8


def test_named_weapon_enhancement_compiles_with_versatile_profile() -> None:
    importer = _load_importer()
    paragraph = (
        "<strong>Quarterstaff.</strong> Melee Weapon Attack: +2 to hit (+4 to hit with shillelagh), "
        "reach 5 ft., one target. Hit: 3 (1d6) bludgeoning damage, or 4 (1d8) bludgeoning damage "
        "if wielded with two hands, or 6 (1d8 + 2) bludgeoning damage with shillelagh."
    )

    attacks = importer._attacks(paragraph)

    assert [attack["id"] for attack in attacks] == [
        "quarterstaff",
        "quarterstaff-two-handed",
        "quarterstaff-shillelagh",
    ]
    assert all(attack["source_complete"] for attack in attacks)
    enhanced = attacks[2]
    assert enhanced["attack_bonus"] == 4
    assert enhanced["damage"]["dice_count"] == 1
    assert enhanced["damage"]["dice_size"] == 8
    assert enhanced["damage"]["bonus"] == 2


def test_named_weapon_enhancement_compiles_without_other_variant() -> None:
    importer = _load_importer()
    paragraph = (
        "<strong>Club.</strong> Melee Weapon Attack: +2 to hit (+6 to hit with shillelagh), "
        "reach 5 ft., one target. Hit: 2 (1d4) bludgeoning damage, or 8 (1d8 + 4) "
        "bludgeoning damage with shillelagh."
    )

    attacks = importer._attacks(paragraph)

    assert [attack["id"] for attack in attacks] == ["club", "club-shillelagh"]
    assert all(attack["source_complete"] for attack in attacks)
    enhanced = attacks[1]
    assert enhanced["attack_bonus"] == 6
    assert enhanced["damage"]["dice_size"] == 8
    assert enhanced["damage"]["bonus"] == 4


def test_2014_versatile_weapon_uses_highest_legal_damage_mode() -> None:
    # Free second hand: use the stronger versatile profile.
    assert select_damage_mode_2014("quarterstaff", second_hand_free=True) == (1, 8, None)

    # Shield/occupied hand: the versatile profile is illegal, so use one-handed damage.
    assert select_damage_mode_2014("quarterstaff", second_hand_free=False) == (1, 6, None)


def test_2014_two_handed_weapon_is_illegal_with_occupied_second_hand() -> None:
    with pytest.raises(ValueError, match="requires two hands"):
        select_damage_mode_2014("greatsword", second_hand_free=False)
