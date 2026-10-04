from __future__ import annotations

import logging

from app.domain.melee_hit_save_retaliation import MeleeHitSaveRetaliation
from app.domain.timed_self_buffs import TimedFriendlySaveAura, TimedSelfBuffAction

logger = logging.getLogger(__name__)


def _holy_aura(save_dc: int, *, bind_blind_to_source: bool) -> TimedSelfBuffAction:
    if not 1 <= save_dc <= 40:
        raise ValueError("Holy Aura requires a certified spell save DC.")
    return TimedSelfBuffAction(
        id="holy-aura",
        name="Holy Aura",
        action_cost="action",
        resource_id="spell-slot-8",
        resource_cost=1,
        duration_rounds=10,
        concentration=True,
        priority=50,
        animation="holy-aura",
        friendly_save_advantage_aura=TimedFriendlySaveAura(
            radius_ft=30,
            all_saves=True,
            attacks_against_disadvantage=True,
            melee_hit_save_retaliation=MeleeHitSaveRetaliation(
                attacker_creature_types=["fiend", "undead"],
                save_ability="constitution",
                save_dc=save_dc,
                condition_id="blinded",
                expiry_timing="target_turn_end",
                duration_rounds=1,
                bind_to_source_effect=bind_blind_to_source,
            ),
        ),
    )


def holy_aura_2024(save_dc: int) -> TimedSelfBuffAction:
    """2024 Holy Aura: ally save Advantage, attacks-against Disadvantage, Fiend/Undead Blind until next turn."""
    try:
        return _holy_aura(save_dc, bind_blind_to_source=False)
    except Exception:
        logger.exception("Failed to build 2024 Holy Aura.")
        raise


def holy_aura_2014(save_dc: int) -> TimedSelfBuffAction:
    """2014 Holy Aura: same aura; Fiend/Undead Blind lasts until the spell ends."""
    try:
        return _holy_aura(save_dc, bind_blind_to_source=True)
    except Exception:
        logger.exception("Failed to build 2014 Holy Aura.")
        raise
