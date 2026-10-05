from __future__ import annotations

from app.content.certified_heroes import build_certified_hero_templates_for_ruleset
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.pregen_weapon_source_qualifiers import (
    apply_canonical_pregen_weapon_source_qualifiers,
    canonical_pregen_weapon_source_qualifiers,
)
from app.domain.damage_sources import DamageSourceQualifier


def test_canonical_pregen_weapon_bands_are_mundane_silvered_then_magical() -> None:
    assert canonical_pregen_weapon_source_qualifiers(1) == []
    assert canonical_pregen_weapon_source_qualifiers(2) == []
    assert canonical_pregen_weapon_source_qualifiers(3) == [DamageSourceQualifier.SILVERED]
    assert canonical_pregen_weapon_source_qualifiers(4) == [DamageSourceQualifier.SILVERED]
    assert canonical_pregen_weapon_source_qualifiers(5) == [DamageSourceQualifier.MAGICAL]
    assert canonical_pregen_weapon_source_qualifiers(20) == [DamageSourceQualifier.MAGICAL]


def test_loadout_qualifiers_stamp_manufactured_weapons_but_not_unarmed_strikes() -> None:
    fighter = apply_canonical_pregen_weapon_source_qualifiers(build_karnok_stoneward_2014(5))
    assert DamageSourceQualifier.MAGICAL in fighter.weapon_attack.damage_source_qualifiers
    assert fighter.weapon_attack.weapon.id == "greatsword"

    monk = apply_canonical_pregen_weapon_source_qualifiers(build_kael_stillwater_2014(5))
    assert monk.weapon_attack.weapon.id == "unarmed-strike"
    assert DamageSourceQualifier.MAGICAL not in monk.weapon_attack.damage_source_qualifiers
    shortsword = monk.alternate_weapon_attacks[0]
    assert shortsword.weapon.id == "shortsword"
    assert DamageSourceQualifier.MAGICAL in shortsword.damage_source_qualifiers


def _is_unarmed(attack) -> bool:
    return attack.weapon.id == "unarmed-strike" or attack.weapon.name.casefold() == "unarmed strike"


def test_certified_2014_and_2024_fighters_carry_the_canonical_weapon_bands() -> None:
    heroes_2014 = {item.level: item for item in build_certified_hero_templates_for_ruleset("2014") if item.id.startswith("karnok-stoneward-2014")}
    heroes_2024 = {item.level: item for item in build_certified_hero_templates_for_ruleset("2024") if item.id.startswith("karnok-stoneward-l")}

    assert DamageSourceQualifier.SILVERED not in heroes_2014[1].weapon_attack.damage_source_qualifiers
    assert DamageSourceQualifier.MAGICAL not in heroes_2014[1].weapon_attack.damage_source_qualifiers
    assert DamageSourceQualifier.SILVERED in heroes_2014[3].weapon_attack.damage_source_qualifiers
    assert DamageSourceQualifier.MAGICAL in heroes_2014[5].weapon_attack.damage_source_qualifiers
    assert DamageSourceQualifier.MAGICAL in heroes_2014[20].weapon_attack.damage_source_qualifiers

    assert DamageSourceQualifier.SILVERED in heroes_2024[3].weapon_attack.damage_source_qualifiers
    assert DamageSourceQualifier.MAGICAL in heroes_2024[5].weapon_attack.damage_source_qualifiers


def test_all_certified_manufactured_weapons_follow_the_loadout_band() -> None:
    band = {
        level: tuple(item.value for item in canonical_pregen_weapon_source_qualifiers(level))
        for level in range(1, 21)
    }
    seen_bands: dict[int, set[tuple[str, ...]]] = {level: set() for level in range(1, 21)}
    for ruleset in ("2014", "2024"):
        heroes = build_certified_hero_templates_for_ruleset(ruleset)
        assert len(heroes) == 240
        for hero in heroes:
            granted = set(canonical_pregen_weapon_source_qualifiers(hero.level))
            for attack in [hero.weapon_attack, *hero.alternate_weapon_attacks]:
                quals = set(attack.damage_source_qualifiers)
                if _is_unarmed(attack):
                    assert DamageSourceQualifier.SILVERED not in quals
                    continue
                assert granted <= quals
                seen_bands[hero.level].add(band[hero.level])
    assert seen_bands[1] == {()}
    assert seen_bands[2] == {()}
    assert seen_bands[3] == {("silvered",)}
    assert seen_bands[4] == {("silvered",)}
    for level in range(5, 21):
        assert seen_bands[level] == {("magical",)}
