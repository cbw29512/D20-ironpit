from __future__ import annotations

import pytest

from app.content.attack_bonus_rules import archery_fighting_style_bonus, compile_weapon_attack_bonus
from app.content.pregens import build_brom_ironmark, build_selene_asharrow
from app.domain.models import WeaponAttackKind


def test_archery_adds_two_only_to_ranged_weapons() -> None:
    assert archery_fighting_style_bonus("Archery", WeaponAttackKind.RANGED) == 2
    assert archery_fighting_style_bonus("Archery", WeaponAttackKind.MELEE) == 0
    assert archery_fighting_style_bonus("Defense", WeaponAttackKind.RANGED) == 0


def test_archery_compiles_level_one_longbow_attack_from_base_five_to_seven() -> None:
    assert compile_weapon_attack_bonus(5, "Archery", WeaponAttackKind.RANGED) == 7
    selene = build_selene_asharrow()
    assert selene.fighting_style == "Archery"
    assert selene.weapon_attack.weapon.attack_kind is WeaponAttackKind.RANGED
    assert selene.weapon_attack.attack_bonus == 7


def test_archery_does_not_change_melee_attack_bonus() -> None:
    assert compile_weapon_attack_bonus(5, "Archery", WeaponAttackKind.MELEE) == 5
    brom = build_brom_ironmark()
    assert brom.weapon_attack.weapon.attack_kind is WeaponAttackKind.MELEE
    assert brom.weapon_attack.attack_bonus == 5


def test_archery_rejects_untyped_weapon_kind() -> None:
    with pytest.raises(ValueError, match="typed weapon attack kind"):
        archery_fighting_style_bonus("Archery", "ranged")  # type: ignore[arg-type]
