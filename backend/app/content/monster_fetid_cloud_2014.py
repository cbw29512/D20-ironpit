"""Source-proven 2014 monster gas zones, preserving the printed combat terms.

The reusable zone resolver owns combat semantics; this module only verifies
that an immutable monster card supplies exactly the source parameters.
"""
from __future__ import annotations

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.persistent_save_zones import PersistentSaveZoneAction
from app.domain.combatants import ResourceDefinition


def fetid_cloud_zone_2014(monster: SourceMonster2014) -> PersistentSaveZoneAction | None:
    if "Fetid Cloud (1/Day)" not in monster.action_names:
        return None
    printed = source_sections_2014(monster.source_actions).get("Fetid Cloud (1/Day)", "").casefold()
    required = (
        "10", "radius", "1 minute", "starts its turn", "dc 11 constitution",
        "poisoned until the start of its next turn",
        "either an action or a bonus action", "can't take reactions",
    )
    if not all(fragment in printed for fragment in required):
        return None
    return PersistentSaveZoneAction(
        id="fetid-cloud", name="Fetid Cloud (1/Day)", level=0,
        action_cost="action", cast_range_ft=0, center_on_source=True, follows_source=True,
        radius_ft=10, duration_rounds=10, save_ability="constitution",
        dc=11, triggers=["start_turn"], target_policy="all",
        save_context="nonmagical", failed_save_condition_id="poisoned",
        failed_save_duration_rounds=1, failed_save_expiry_timing="target_turn_start",
        failed_save_action_bonus_exclusive=True,
        failed_save_suppress_reactions=True,
        resource_id="fetid-cloud", resource_cost=1,
        animation="fetid-cloud", source="SRD 5.1 (2014)",
    )


def fetid_cloud_resources_2014(monster: SourceMonster2014) -> list[ResourceDefinition]:
    if fetid_cloud_zone_2014(monster) is None:
        return []
    return [ResourceDefinition(id="fetid-cloud", name="Fetid Cloud", max_uses=1)]
