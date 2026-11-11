"""2014 printed barrier -> generic persistent barrier action card parameters.

The source's creation and destroyed-section damage saves remain separately
blocked until the shared combat turn pipeline can resolve both. Registering
the card cannot by itself grant source-admission status.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_barrier_2014 import source_barrier_parameters_2014
from app.domain.persistent_barriers import PersistentBarrierAction
from app.domain.actions import SavingThrowAction

logger = logging.getLogger(__name__)


def source_barrier_actions_2014(monster: SourceMonster2014) -> list[PersistentBarrierAction]:
    """Compile source-exact wall material, section durability, and Recharge cost."""
    try:
        verified = source_barrier_parameters_2014(monster)
        if verified is None:
            return []
        return [PersistentBarrierAction(
            id=verified.action_id,
            name=verified.source_name,
            level=0,
            action_cost="action",
            resource_id=verified.action_id,
            resource_cost=1,
            cast_range_ft=verified.cast_range_ft,
            concentration=False,
            duration_rounds=verified.duration_rounds,
            permanent_after_full_duration=False,
            min_sections=1,
            max_sections=verified.max_wall_length_ft // verified.section_length_ft,
            sections_must_be_contiguous=True,
            section_length_ft=verified.section_length_ft,
            section_height_ft=verified.wall_height_ft,
            section_thickness_inches=12,
            armor_class=verified.section_ac,
            hit_points_per_section=verified.section_hp,
            damage_immunities=list(verified.damage_immunities),
            damage_vulnerabilities=["fire"] if verified.fire_vulnerable else [],
            on_creation_save=SavingThrowAction(
                id=verified.action_id, name=verified.source_name,
                save_ability=verified.creation_save_ability,
                dc=verified.creation_save_dc, range_ft=verified.cast_range_ft,
                damage_dice_count=10, damage_dice_size=6,
                damage_type="cold", success_damage="half", magical_effect=True,
                target_scope="all-other-creatures", max_targets=12,
            ),
            destroyed_section_crossing_save=SavingThrowAction(
                id=verified.action_id, name=verified.source_name,
                save_ability=verified.cross_destroyed_section_save_ability,
                dc=verified.cross_destroyed_section_dc, range_ft=0,
                damage_dice_count=5, damage_dice_size=6,
                damage_type="cold", success_damage="half", magical_effect=True,
                target_scope="all-other-creatures", max_targets=12,
            ),
            blocks_movement=True,
            blocks_line_of_sight=True,
            ends_on_source_incapacitated=verified.ends_when_source_incapacitated,
            ends_on_source_death=verified.ends_when_source_dead,
            material="ice",
            source="SRD 5.1 (2014): " + verified.source_name,
        )]
    except Exception:
        logger.exception("Failed source-verified 2014 barrier card for %s", monster.id)
        raise
