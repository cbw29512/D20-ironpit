from __future__ import annotations

import logging

from app.combat.suppression_zone_geometry import covering_zones
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.combat.timed_conditions import apply_timed_condition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)
_ZONE_DEAFEN = "suppression-zone-deafen"


def expire_suppression_zones(setup: EncounterSetup, round_number: int) -> None:
    try:
        setup.suppression_zones = [
            zone for zone in setup.suppression_zones if zone.expires_round > round_number
        ]
    except Exception:
        logger.exception("Failed to expire suppression zones at round %s.", round_number)
        raise


def sync_suppression_zone_effects(setup: EncounterSetup, round_number: int = 1) -> None:
    """Apply live Silence-style deafening and thunder immunity while inside a zone."""
    try:
        for member in [*setup.heroes, *setup.monsters]:
            zones = covering_zones(member, setup)
            _sync_zone_deafen(member, any(zone.deafens for zone in zones), round_number)
            thunder = any(zone.thunder_immunity for zone in zones)
            immunities = [
                item for item in member.state.zone_damage_immunities if item is not DamageType.THUNDER
            ]
            if thunder:
                immunities.append(DamageType.THUNDER)
            member.state.zone_damage_immunities = immunities
    except Exception:
        logger.exception("Failed to sync suppression-zone effects.")
        raise


def _sync_zone_deafen(member: EncounterCombatant, deafened: bool, round_number: int) -> None:
    owned = [
        effect
        for effect in member.state.timed_effects
        if effect.source_effect_id == _ZONE_DEAFEN
    ]
    if deafened and not owned:
        apply_timed_condition(
            member.state,
            "deafened",
            "suppression-zone",
            source_effect_id=_ZONE_DEAFEN,
            applied_round=round_number,
            expiry_timing=None,
            expires_at_start_of_source_turn=False,
            use_default_poison_recovery=False,
        )
        return
    if deafened:
        return
    for effect in owned:
        remove_effect_instance(member.state, effect)
