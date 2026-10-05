from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def test_octopus_ink_cloud_is_absent_water_and_tentacles_grapple() -> None:
    roster_ids = {item.id for item in build_basic_2014_monsters()}
    expected = {
        "octopus": (10, False),
        "giant-octopus": (16, True),
    }
    for monster_id, (escape_dc, restrains) in expected.items():
        source = _source(monster_id)
        assert basic_blockers_2014(source) == ()
        assert any(name.startswith("Ink Cloud") for name in source.action_names)
        assert f"2014-{monster_id}" in roster_ids
        template = compile_combatant(adapt_basic_monster_2014(source))
        grapple = template.weapon_attack.control_effect
        assert grapple is not None
        assert grapple.grapple_escape_dc == escape_dc
        assert grapple.restrains_while_grappled is restrains
        assert template.weapon_attack.forbid_target_grappled_by_self is True
        assert template.recharge_rules == []


def test_blink_dog_teleport_plus_bite_stays_parked() -> None:
    source = _source("blink-dog")
    assert source.action_recharges == {"teleport": 4}
    assert "mechanic:recharge" in basic_blockers_2014(source)
    assert "2014-blink-dog" not in {item.id for item in build_basic_2014_monsters()}


def test_swallow_attach_and_pull_remain_parked() -> None:
    parked = {
        "giant-frog": "mechanic:swallow",
        "giant-toad": "mechanic:swallow",
        "stirge": "attack:complex",
        "roper": "source:extra-action",
        "blink-dog": "mechanic:recharge",
    }
    for monster_id, blocker in parked.items():
        assert blocker in basic_blockers_2014(_source(monster_id))
