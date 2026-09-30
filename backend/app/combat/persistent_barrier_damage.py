from __future__ import annotations

import logging
from dataclasses import dataclass

from app.domain.encounters import EncounterSetup
from app.domain.persistent_barriers import PersistentBarrierSectionState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BarrierDamageResult:
    barrier_id: str
    section_id: str
    requested_damage: int
    applied_damage: int
    hp_before: int
    hp_after: int
    destroyed: bool
    immune: bool


def _section(
    setup: EncounterSetup,
    barrier_id: str,
    section_id: str,
) -> PersistentBarrierSectionState:
    try:
        barrier = next(
            (item for item in setup.persistent_barriers if item.barrier_id == barrier_id),
            None,
        )
        if barrier is None:
            raise ValueError(f"Unknown persistent barrier {barrier_id!r}.")
        section = next(
            (item for item in barrier.sections if item.section_id == section_id),
            None,
        )
        if section is None:
            raise ValueError(f"Unknown barrier section {section_id!r}.")
        return section
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to load barrier section %s.", section_id)
        raise RuntimeError("Barrier section could not be loaded.") from exc


def apply_barrier_section_damage(
    setup: EncounterSetup,
    barrier_id: str,
    section_id: str,
    damage: int,
    damage_type: str,
) -> BarrierDamageResult:
    """Apply already-resolved damage to one destructible barrier section."""
    try:
        if damage < 0:
            raise ValueError("Barrier damage cannot be negative.")
        section = _section(setup, barrier_id, section_id)
        hp_before = section.current_hp
        immune = damage_type in set(section.damage_immunities)
        applied = 0 if immune or section.destroyed else min(damage, section.current_hp)
        section.current_hp = max(0, section.current_hp - applied)
        if section.current_hp == 0:
            section.destroyed = True
        return BarrierDamageResult(
            barrier_id=barrier_id,
            section_id=section_id,
            requested_damage=damage,
            applied_damage=applied,
            hp_before=hp_before,
            hp_after=section.current_hp,
            destroyed=section.destroyed,
            immune=immune,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to apply damage to barrier section %s.", section_id)
        raise RuntimeError("Barrier section damage could not be resolved.") from exc
