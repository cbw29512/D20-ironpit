from __future__ import annotations

from app.content.monster_fetid_cloud_2014 import fetid_cloud_zone_2014, fetid_cloud_resources_2014
from app.content.monster_source_2014 import load_monster_source_2014


def test_fetid_cloud_source_binds_exact_universal_nonspell_controls() -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == "dretch")
    before = monster.model_dump_json()
    zone = fetid_cloud_zone_2014(monster)
    assert zone is not None
    assert zone.center_on_source and zone.radius_ft == 10
    assert zone.target_policy == "all"
    assert zone.save_context == "nonmagical"
    assert zone.triggers == ["start_turn"]
    assert zone.dc == 11
    assert zone.failed_save_condition_id == "poisoned"
    assert zone.failed_save_action_bonus_exclusive
    assert zone.failed_save_suppress_reactions
    assert zone.duration_rounds == 10
    assert zone.resource_id == "fetid-cloud"
    assert fetid_cloud_resources_2014(monster)[0].max_uses == 1
    assert monster.model_dump_json() == before


def test_missing_or_drifted_printed_source_fails_closed() -> None:
    monster = next(m for m in load_monster_source_2014() if m.id == "dretch")
    edited = monster.model_copy(update={
        "source_actions": (monster.source_actions or "").replace(
            "can't take reactions", "can take reactions"
        ),
    })
    assert fetid_cloud_zone_2014(edited) is None
    assert fetid_cloud_resources_2014(edited) == []
