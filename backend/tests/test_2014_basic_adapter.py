from app.content.capability_compiler import compile_combatant
from app.content.monster_capabilities_2014 import load_2014_mvp_definitions
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import SourceMonster2014, load_monster_source_2014


def _attacks(definition):
    return {
        attack.name: (
            attack.attack_bonus,
            attack.damage.count,
            attack.damage.size,
            attack.damage.bonus,
            attack.damage_type,
            attack.reach_ft,
            attack.normal_range_ft,
            attack.long_range_ft,
        )
        for attack in definition.attacks
    }


def _slots(definition):
    if not definition.attack_action:
        return []
    by_id = {attack.id: attack.name for attack in definition.attacks}
    return [[by_id[item] for item in slot.attack_ids] for slot in definition.attack_action.slots]


def _movement(definition):
    modes = definition.movement_modes
    if modes is None:
        return (definition.speed_ft, 0, 0, 0, 0, False)
    return (
        modes.walk_ft,
        modes.fly_ft,
        modes.climb_ft,
        modes.swim_ft,
        modes.burrow_ft,
        modes.hover,
    )


def test_bulk_adapter_preserves_hand_certified_mvp_combat_semantics():
    source = {monster.id: monster for monster in load_monster_source_2014()}
    hand = load_2014_mvp_definitions()
    for source_id in ("goblin", "bandit", "skeleton", "brown-bear"):
        adapted = adapt_basic_monster_2014(source[source_id])
        expected = hand[f"2014-{source_id}"]
        assert adapted.ruleset == expected.ruleset == "2014"
        assert adapted.creature_type == source[source_id].creature_type
        assert compile_combatant(adapted).creature_type == source[source_id].creature_type
        assert adapted.armor_class == expected.armor_class
        assert adapted.max_hp == expected.max_hp
        assert adapted.speed_ft == expected.speed_ft
        assert _movement(adapted) == _movement(expected)
        assert adapted.initiative_bonus == expected.initiative_bonus
        assert _attacks(adapted) == _attacks(expected)
        assert _slots(adapted) == _slots(expected)
        assert adapted.source_trait_names == expected.source_trait_names
        assert adapted.damage_resistances == expected.damage_resistances
        assert adapted.damage_vulnerabilities == expected.damage_vulnerabilities
        assert adapted.damage_immunities == expected.damage_immunities
        assert adapted.condition_immunities == expected.condition_immunities


def _choice_slot_fixture() -> SourceMonster2014:
    return SourceMonster2014.model_validate({
        "id": "choice-slot-fixture",
        "name": "Choice Slot Fixture",
        "ruleset": "2014",
        "size": "Medium",
        "creature_type": "humanoid",
        "armor_class": 13,
        "max_hp": 20,
        "speed": {"walk": 30},
        "abilities": {"str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10},
        "attacks": [
            {
                "id": "blade",
                "name": "Blade",
                "kind": "melee",
                "attack_bonus": 4,
                "damage": {"average": 5, "dice_count": 1, "dice_size": 6, "bonus": 2, "type": "slashing"},
            },
            {
                "id": "bow",
                "name": "Bow",
                "kind": "ranged",
                "attack_bonus": 4,
                "damage": {"average": 5, "dice_count": 1, "dice_size": 6, "bonus": 2, "type": "piercing"},
                "normal_range_ft": 80,
                "long_range_ft": 320,
            },
        ],
        "multiattack_slots": [["blade", "bow"], ["blade", "bow"]],
        "action_names": ["Multiattack", "Blade", "Bow"],
    })


def test_2014_choice_slot_reuses_existing_multiattack_choice_primitive() -> None:
    source = _choice_slot_fixture()
    assert "multiattack:choice-or-binding" not in basic_blockers_2014(source)
    definition = adapt_basic_monster_2014(source)
    assert definition.attack_action is not None
    assert [slot.attack_ids for slot in definition.attack_action.slots] == [
        ["2014-choice-slot-fixture-blade", "2014-choice-slot-fixture-bow"],
        ["2014-choice-slot-fixture-blade", "2014-choice-slot-fixture-bow"],
    ]
    runtime = compile_combatant(definition)
    assert [slot.attack_ids for slot in runtime.attack_action.slots] == [
        ["2014-choice-slot-fixture-blade", "2014-choice-slot-fixture-bow"],
        ["2014-choice-slot-fixture-blade", "2014-choice-slot-fixture-bow"],
    ]


def test_2014_choice_slot_still_fails_closed_for_unknown_attack_ids() -> None:
    source = _choice_slot_fixture().model_copy(update={
        "multiattack_slots": [["blade", "missing-attack"]],
    })
    assert "multiattack:choice-or-binding" in basic_blockers_2014(source)
