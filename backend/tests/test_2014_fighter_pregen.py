from __future__ import annotations

from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.certified_heroes_2014 import build_certified_hero_entries_2014
from app.content.fighter_2014_progression import build_karnok_stoneward_2014_level
from app.domain.models import RollMode
from app.domain.traits import CombatTrait


def _resources(level: int) -> dict[str, int]:
    template = build_karnok_stoneward_2014_level(level)
    return {item.id: item.max_uses for item in template.resources}


def test_2014_champion_is_contiguous_levels_one_through_ten() -> None:
    entries = build_certified_hero_entries_2014()
    assert [key[1] for key, _ in entries] == list(range(1, 11))
    assert all(template.ruleset == "2014" for _, template in entries)
    assert all(template.kind == "character" for _, template in entries)
    assert all(template.weapon_masteries == [] for _, template in entries)
    assert all(
        attack.weapon.mastery_property is None
        for _, template in entries
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
    )


def test_2014_fighter_progression_uses_2014_resource_and_feature_timing() -> None:
    assert _resources(1) == {"second-wind": 1, "relentless-endurance": 1}
    assert _resources(2) == {"second-wind": 1, "action-surge": 1, "relentless-endurance": 1}
    assert _resources(9) == {
        "second-wind": 1,
        "action-surge": 1,
        "indomitable": 1,
        "relentless-endurance": 1,
    }
    level3 = build_karnok_stoneward_2014_level(3)
    level5 = build_karnok_stoneward_2014_level(5)
    level7 = build_karnok_stoneward_2014_level(7)
    level9 = build_karnok_stoneward_2014_level(9)
    level10 = build_karnok_stoneward_2014_level(10)
    assert level3.progression_features.critical_hit_minimum == 19
    assert level5.attack_action is not None and len(level5.attack_action.slots) == 2
    assert level7.initiative_bonus == 3
    assert level7.progression_features.initiative_advantage is False
    assert level9.progression_features.indomitable_bonus == 0
    assert level10.fighting_styles == ["Defense", "Archery"]
    shortbow = next(item for item in level10.alternate_weapon_attacks if item.weapon.id == "shortbow")
    assert shortbow.attack_bonus == 7


def test_2014_half_orc_traits_do_not_import_2024_origin_features() -> None:
    template = build_karnok_stoneward_2014_level(10)
    assert set(template.combat_traits) == {CombatTrait.SAVAGE_ATTACKS, CombatTrait.RELENTLESS_ENDURANCE}
    assert CombatTrait.SAVAGE_ATTACKER not in template.combat_traits
    assert template.progression_features.tactical_shift_fraction == 0
    assert template.progression_features.tactical_master_sap_weapon_ids == []
    assert template.progression_features.great_weapon_fighting is False


def test_2014_savage_attacks_adds_exactly_one_melee_weapon_die_on_critical() -> None:
    template = build_karnok_stoneward_2014_level(3)
    state = build_combatant_state(template)
    roll, components = resolve_weapon_damage(
        state,
        template.weapon_attack,
        FixedDiceProvider([1, 2, 3, 4, 5]),
        critical=True,
        attack_mode=RollMode.NORMAL,
    )
    assert roll.rolls == [1, 2, 3, 4, 5]
    assert components[0].notation == "4d6+3"
    assert components[1].source == "Savage Attacks"
    assert components[1].notation == "1d6+0"


def test_2014_savage_attacks_does_not_apply_to_ranged_critical_or_normal_melee_hit() -> None:
    template = build_karnok_stoneward_2014_level(3)
    state = build_combatant_state(template)
    shortbow = template.alternate_weapon_attacks[0]
    _, ranged_components = resolve_weapon_damage(
        state, shortbow, FixedDiceProvider([1, 2]), critical=True, attack_mode=RollMode.NORMAL,
    )
    _, normal_components = resolve_weapon_damage(
        state, template.weapon_attack, FixedDiceProvider([1, 2]), critical=False, attack_mode=RollMode.NORMAL,
    )
    assert [item.source for item in ranged_components] == ["Shortbow"]
    assert [item.source for item in normal_components] == ["Greatsword"]
