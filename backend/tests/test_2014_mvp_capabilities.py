import pytest

from app.combat.attacks import resolve_attack
from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monster_capabilities_2014 import (
    build_2014_mvp_monsters,
    load_2014_mvp_definitions,
)
from app.content.roster import build_arena_roster
from app.domain.models import DamageType


def _monsters():
    return {item.id: item for item in build_2014_mvp_monsters()}


def test_2014_mvp_source_facts_compile_through_universal_schema() -> None:
    definitions = load_2014_mvp_definitions()
    assert set(definitions) == {"2014-bandit", "2014-skeleton", "2014-brown-bear"}
    assert all(item.ruleset == "2014" and item.kind == "monster" for item in definitions.values())

    bandit = definitions["2014-bandit"]
    assert (bandit.armor_class, bandit.max_hp, bandit.speed_ft, bandit.challenge_rating) == (12, 11, 30, "1/8")
    assert [(item.name, item.attack_bonus) for item in bandit.attacks] == [("Scimitar", 3), ("Light Crossbow", 3)]

    skeleton = definitions["2014-skeleton"]
    assert (skeleton.armor_class, skeleton.max_hp, skeleton.speed_ft, skeleton.challenge_rating) == (13, 13, 30, "1/4")
    assert skeleton.damage_vulnerabilities == [DamageType.BLUDGEONING]
    assert skeleton.damage_immunities == [DamageType.POISON]
    assert skeleton.condition_immunities == ["exhaustion", "poisoned"]

    bear = definitions["2014-brown-bear"]
    assert (bear.armor_class, bear.max_hp, bear.speed_ft, bear.challenge_rating) == (11, 34, 40, "1")
    assert bear.movement_modes is not None and bear.movement_modes.climb_ft == 30
    assert bear.source_trait_names == ["Keen Smell"]


def test_2014_bandit_ranged_attack_uses_universal_attack_resolver() -> None:
    monsters = _monsters()
    attacker = build_combatant_state(monsters["2014-bandit"])
    defender = build_combatant_state(monsters["2014-skeleton"])
    crossbow = attacker.template.alternate_weapon_attacks[0]

    event = resolve_attack(1, 1, attacker, defender, crossbow, 80, FixedDiceProvider([10, 4]))

    assert event.hit is True
    assert defender.current_hp == 8


def test_2014_skeleton_defenses_use_shared_damage_engine() -> None:
    skeleton = build_combatant_state(_monsters()["2014-skeleton"])
    assert adjusted_damage_amount(5, DamageType.BLUDGEONING, skeleton) == 10
    assert adjusted_damage_amount(5, DamageType.POISON, skeleton) == 0
    assert adjusted_damage_amount(5, DamageType.PIERCING, skeleton) == 5


def test_2014_brown_bear_uses_universal_ordered_multiattack() -> None:
    bear = _monsters()["2014-brown-bear"]
    assert bear.ruleset == "2014"
    assert bear.attack_action is not None
    assert [slot.attack_ids for slot in bear.attack_action.slots] == [
        ["2014-brown-bear-bite"],
        ["2014-brown-bear-claws"],
    ]
    assert bear.movement_modes.climb_ft == 30
    assert bear.combat_traits == []
    assert bear.weapon_masteries == []
    assert bear.source_trait_names == ["Keen Smell"]


def test_2014_mvp_slice_is_not_admitted_into_2024_production_roster() -> None:
    mvp_ids = set(_monsters())
    production = build_arena_roster("2024")
    production_ids = {item.id for item in production.monsters}
    assert mvp_ids.isdisjoint(production_ids)
    assert all(item.ruleset == "2024" for item in production.monsters)

    with pytest.raises(ValueError, match="2014 roster is not admitted"):
        build_arena_roster("2014")
