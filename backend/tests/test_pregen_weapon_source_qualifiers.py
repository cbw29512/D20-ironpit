from __future__ import annotations

from app.content.certified_heroes import build_certified_hero_templates_for_ruleset
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.pregen_weapon_source_qualifiers import (
    apply_canonical_pregen_weapon_source_qualifiers,
    canonical_pregen_weapon_plus_bonus,
    canonical_pregen_weapon_source_qualifiers,
)
from app.domain.damage_sources import DamageSourceQualifier


def test_fixed_ladder_uses_silvered_then_table_f_g_h() -> None:
    for level in (1, 2, 3, 4):
        assert canonical_pregen_weapon_plus_bonus(level) == 0
        assert canonical_pregen_weapon_source_qualifiers(level) == [DamageSourceQualifier.SILVERED]
    for level in (5, 10):
        assert canonical_pregen_weapon_plus_bonus(level) == 1
        assert canonical_pregen_weapon_source_qualifiers(level) == [DamageSourceQualifier.MAGICAL]
    for level in (11, 16):
        assert canonical_pregen_weapon_plus_bonus(level) == 2
        assert canonical_pregen_weapon_source_qualifiers(level) == [DamageSourceQualifier.MAGICAL]
    for level in (17, 20):
        assert canonical_pregen_weapon_plus_bonus(level) == 3
        assert canonical_pregen_weapon_source_qualifiers(level) == [DamageSourceQualifier.MAGICAL]


def test_silvered_adds_no_hit_or_damage_and_plus_n_keeps_dice() -> None:
    raw1 = build_karnok_stoneward_2014(1)
    silvered = apply_canonical_pregen_weapon_source_qualifiers(raw1)
    assert silvered.weapon_attack.damage_source_qualifiers == [DamageSourceQualifier.SILVERED]
    assert silvered.weapon_attack.attack_bonus == raw1.weapon_attack.attack_bonus
    assert silvered.weapon_attack.damage_bonus == raw1.weapon_attack.damage_bonus
    assert (
        silvered.weapon_attack.weapon.dice_count,
        silvered.weapon_attack.weapon.dice_size,
    ) == (raw1.weapon_attack.weapon.dice_count, raw1.weapon_attack.weapon.dice_size)

    raw5 = build_karnok_stoneward_2014(5)
    plus_one = apply_canonical_pregen_weapon_source_qualifiers(raw5)
    assert plus_one.weapon_attack.damage_source_qualifiers == [DamageSourceQualifier.MAGICAL]
    assert plus_one.weapon_attack.attack_bonus == raw5.weapon_attack.attack_bonus + 1
    assert plus_one.weapon_attack.damage_bonus == raw5.weapon_attack.damage_bonus + 1

    raw11 = build_karnok_stoneward_2014(11)
    plus_two = apply_canonical_pregen_weapon_source_qualifiers(raw11)
    assert plus_two.weapon_attack.attack_bonus == raw11.weapon_attack.attack_bonus + 2
    assert plus_two.weapon_attack.damage_bonus == raw11.weapon_attack.damage_bonus + 2

    raw17 = build_karnok_stoneward_2014(17)
    plus_three = apply_canonical_pregen_weapon_source_qualifiers(raw17)
    assert plus_three.weapon_attack.attack_bonus == raw17.weapon_attack.attack_bonus + 3
    assert plus_three.weapon_attack.damage_bonus == raw17.weapon_attack.damage_bonus + 3


def test_loadout_skips_unarmed_strikes() -> None:
    monk_base = build_kael_stillwater_2014(5)
    monk = apply_canonical_pregen_weapon_source_qualifiers(monk_base)
    assert monk.weapon_attack.weapon.id == "unarmed-strike"
    assert monk.weapon_attack.attack_bonus == monk_base.weapon_attack.attack_bonus
    assert DamageSourceQualifier.SILVERED not in monk.weapon_attack.damage_source_qualifiers
    shortsword = monk.alternate_weapon_attacks[0]
    assert shortsword.damage_source_qualifiers == [DamageSourceQualifier.MAGICAL]
    assert shortsword.attack_bonus == monk_base.alternate_weapon_attacks[0].attack_bonus + 1


def test_weapon_plus_stamp_is_idempotent() -> None:
    first = apply_canonical_pregen_weapon_source_qualifiers(build_karnok_stoneward_2014(5))
    second = apply_canonical_pregen_weapon_source_qualifiers(first)
    assert second.weapon_attack.attack_bonus == first.weapon_attack.attack_bonus
    assert second.weapon_attack.damage_bonus == first.weapon_attack.damage_bonus


def _is_unarmed(attack) -> bool:
    return attack.weapon.id == "unarmed-strike" or attack.weapon.name.casefold() == "unarmed strike"


def test_certified_fighters_follow_fixed_hoard_ladder() -> None:
    expected = {1: 0, 4: 0, 5: 1, 11: 2, 20: 3}
    raw = {level: build_karnok_stoneward_2014(level) for level in expected}
    heroes = {item.level: item for item in build_certified_hero_templates_for_ruleset("2014") if item.id.startswith("karnok-stoneward-2014")}
    for level, plus in expected.items():
        quals = list(heroes[level].weapon_attack.damage_source_qualifiers)
        if plus == 0:
            assert quals == [DamageSourceQualifier.SILVERED]
        else:
            assert quals == [DamageSourceQualifier.MAGICAL]
        assert heroes[level].weapon_attack.attack_bonus == raw[level].weapon_attack.attack_bonus + plus
        assert heroes[level].weapon_attack.damage_bonus == raw[level].weapon_attack.damage_bonus + plus


def test_all_certified_manufactured_weapons_use_the_same_level_ladder() -> None:
    for ruleset in ("2014", "2024"):
        heroes = build_certified_hero_templates_for_ruleset(ruleset)
        assert len(heroes) == 240
        for hero in heroes:
            granted = canonical_pregen_weapon_source_qualifiers(hero.level)
            plus = canonical_pregen_weapon_plus_bonus(hero.level)
            for attack in [hero.weapon_attack, *hero.alternate_weapon_attacks]:
                if _is_unarmed(attack):
                    assert DamageSourceQualifier.SILVERED not in attack.damage_source_qualifiers
                    continue
                assert set(granted) <= set(attack.damage_source_qualifiers)
                if plus == 0:
                    assert DamageSourceQualifier.SILVERED in attack.damage_source_qualifiers
                    assert DamageSourceQualifier.MAGICAL not in granted
                else:
                    assert DamageSourceQualifier.MAGICAL in attack.damage_source_qualifiers
                    assert DamageSourceQualifier.SILVERED not in granted
