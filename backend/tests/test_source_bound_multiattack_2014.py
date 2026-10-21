"""Source-owned conditional Multiattack compilation remains generic."""
from app.content.monster_multiattack_2014 import (
    multiattack_blockers_2014, multiattack_2014, source_bound_slots_2014,
)
from app.content.monster_source_2014 import SourceAttack2014, SourceDamage2014, SourceMonster2014


def _monster():
    return SourceMonster2014(
        id="test-creature", name="Test Creature", ruleset="2014", size="large",
        creature_type="aberration", armor_class=14, max_hp=30,
        speed={"walk": 30}, abilities={"str": 16, "dex": 10, "con": 14, "int": 5, "wis": 10, "cha": 5},
        attacks=[SourceAttack2014(
            id="claw", name="Claw", kind="melee", attack_bonus=5,
            damage=SourceDamage2014(average=7, dice_count=1, dice_size=8, bonus=3, type="slashing"),
        )],
        saving_throw_actions=[{
            "id": "grapple-save", "name": "Grapple Save", "save_ability": "constitution",
            "dc": 13, "range_ft": 5,
        }],
        multiattack_binding={"slots": [
            {"action_ids": ["claw"]},
            {"action_ids": ["claw"]},
            {"action_ids": ["grapple-save"], "optional": True,
             "requirement": "source_has_grappled_target"},
        ]},
    )


def test_source_bound_slots_compile_ordered_mixed_actions():
    monster = _monster()
    assert multiattack_blockers_2014(monster) == []
    action = multiattack_2014(monster)
    assert len(action.slots) == 3
    assert [slot.attack_ids for slot in action.slots] == [
        ["2014-test-creature-claw"], ["2014-test-creature-claw"], [],
    ]
    assert action.slots[2].save_action_ids == ["grapple-save"]
    assert action.slots[2].requires_source_grapple is True


def test_source_bound_slots_reject_unresolved_or_unrecognized_conditions():
    monster = _monster()
    monster.multiattack_binding["slots"][2]["action_ids"] = ["unavailable"]
    assert source_bound_slots_2014(monster) is None
    assert multiattack_blockers_2014(monster) == ["multiattack:complex"]
    monster.multiattack_binding["slots"][2]["action_ids"] = ["grapple-save"]
    monster.multiattack_binding["slots"][2]["requirement"] = "invented"
    assert source_bound_slots_2014(monster) is None
