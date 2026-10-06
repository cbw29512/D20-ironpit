from app.content.monster_charm_control import charm_control_rider, charm_control_save_actions_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _monster(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def test_shared_rider_is_incapacitated_until_hit_or_save() -> None:
    rider = charm_control_rider(15, "wisdom")
    assert rider.effect_id == "incapacitated"
    assert rider.ends_on_damage is True
    assert rider.repeat_save_ability == "wisdom"
    assert rider.repeat_save_dc == 15
    assert rider.repeat_save_timing == "target_turn_end"


def test_succubus_charm_binds_without_monster_name_dispatch() -> None:
    succubus = _monster("succubus-incubus")
    actions = charm_control_save_actions_2014(succubus)
    assert len(actions) == 1
    charm = actions[0]
    assert charm.name == "Charm"
    assert (charm.dc, charm.save_ability, charm.range_ft) == (15, "wisdom", 30)
    assert charm.failed_save_timed_effect is not None
    assert charm.failed_save_timed_effect.effect_id == "incapacitated"


def test_ghost_possession_binds_recharge_and_charisma_save() -> None:
    ghost = _monster("ghost")
    actions = charm_control_save_actions_2014(ghost)
    assert len(actions) == 1
    possession = actions[0]
    assert possession.name == "Possession"
    assert (possession.dc, possession.save_ability, possession.range_ft) == (13, "charisma", 5)
    assert possession.resource_id == "possession"
