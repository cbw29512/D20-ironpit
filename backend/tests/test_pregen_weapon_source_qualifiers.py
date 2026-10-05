from __future__ import annotations

from app.content.certified_heroes import build_certified_hero_templates_for_ruleset
from app.content.fighter_champion_2014_runtime import build_karnok_stoneward_2014
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.pregen_weapon_source_qualifiers import (
    apply_canonical_pregen_weapon_source_qualifiers,
    canonical_pregen_weapon_source_qualifiers,
)
from app.domain.damage_sources import DamageSourceQualifier

_DMG_UNCOMMON_LOADOUT = (
    DamageSourceQualifier.SILVERED,
    DamageSourceQualifier.ADAMANTINE,
    DamageSourceQualifier.MAGICAL,
)


def test_canonical_pregen_weapons_follow_dmg_uncommon_from_first() -> None:
    for level in range(1, 21):
        assert canonical_pregen_weapon_source_qualifiers(level) == list(_DMG_UNCOMMON_LOADOUT)


def test_loadout_qualifiers_stamp_manufactured_weapons_but_not_unarmed_strikes() -> None:
    fighter = apply_canonical_pregen_weapon_source_qualifiers(build_karnok_stoneward_2014(1))
    assert fighter.weapon_attack.weapon.id == "greatsword"
    assert set(fighter.weapon_attack.damage_source_qualifiers) >= set(_DMG_UNCOMMON_LOADOUT)

    monk = apply_canonical_pregen_weapon_source_qualifiers(build_kael_stillwater_2014(5))
    assert monk.weapon_attack.weapon.id == "unarmed-strike"
    assert DamageSourceQualifier.SILVERED not in monk.weapon_attack.damage_source_qualifiers
    assert DamageSourceQualifier.ADAMANTINE not in monk.weapon_attack.damage_source_qualifiers
    shortsword = monk.alternate_weapon_attacks[0]
    assert shortsword.weapon.id == "shortsword"
    assert set(shortsword.damage_source_qualifiers) >= set(_DMG_UNCOMMON_LOADOUT)


def _is_unarmed(attack) -> bool:
    return attack.weapon.id == "unarmed-strike" or attack.weapon.name.casefold() == "unarmed strike"


def test_certified_fighters_carry_dmg_uncommon_qualifiers_from_level_1() -> None:
    heroes_2014 = {item.level: item for item in build_certified_hero_templates_for_ruleset("2014") if item.id.startswith("karnok-stoneward-2014")}
    heroes_2024 = {item.level: item for item in build_certified_hero_templates_for_ruleset("2024") if item.id.startswith("karnok-stoneward-l")}
    for level in (1, 4, 5, 20):
        assert set(_DMG_UNCOMMON_LOADOUT) <= set(heroes_2014[level].weapon_attack.damage_source_qualifiers)
        assert set(_DMG_UNCOMMON_LOADOUT) <= set(heroes_2024[level].weapon_attack.damage_source_qualifiers)


def test_all_certified_manufactured_weapons_follow_dmg_uncommon_from_first() -> None:
    expected = tuple(item.value for item in _DMG_UNCOMMON_LOADOUT)
    seen: dict[int, set[tuple[str, ...]]] = {level: set() for level in range(1, 21)}
    for ruleset in ("2014", "2024"):
        heroes = build_certified_hero_templates_for_ruleset(ruleset)
        assert len(heroes) == 240
        for hero in heroes:
            granted = set(canonical_pregen_weapon_source_qualifiers(hero.level))
            for attack in [hero.weapon_attack, *hero.alternate_weapon_attacks]:
                quals = set(attack.damage_source_qualifiers)
                if _is_unarmed(attack):
                    assert DamageSourceQualifier.SILVERED not in quals
                    assert DamageSourceQualifier.ADAMANTINE not in quals
                    continue
                assert granted <= quals
                seen[hero.level].add(expected)
    for level in range(1, 21):
        assert seen[level] == {expected}
