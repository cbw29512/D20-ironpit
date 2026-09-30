from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.grid_geometry import footprints_overlap
from app.combat.modifier_stack import add_modifier
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.runtime import TimedEffect
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)

_ZONE_SIZE_BY_LENGTH = {
    5: CreatureSize.MEDIUM,
    10: CreatureSize.LARGE,
    15: CreatureSize.HUGE,
    20: CreatureSize.GARGANTUAN,
}


def zone_footprint_size(length_ft: int) -> CreatureSize:
    try:
        return _ZONE_SIZE_BY_LENGTH[length_ft]
    except KeyError as exc:
        raise ValueError(
            "Persistent beneficial zones currently require a 5/10/15/20-foot square footprint."
        ) from exc


def _remove_zone_effects(setup: EncounterSetup, zone_id: str) -> None:
    for member in [*setup.heroes, *setup.monsters]:
        member.state.active_modifiers = [
            item for item in member.state.active_modifiers
            if item.source_effect_id != zone_id
        ]
        member.state.timed_effects = [
            item for item in member.state.timed_effects
            if item.source_effect_id != zone_id
        ]


def _source_member(setup: EncounterSetup, source_id: str) -> EncounterCombatant | None:
    return next(
        (
            member
            for member in [*setup.heroes, *setup.monsters]
            if member.combatant_id == source_id
        ),
        None,
    )


def _member_inside_zone(member: EncounterCombatant, zone) -> bool:
    if member.state.position is None:
        return False
    return footprints_overlap(
        member.state.position,
        member.state.template.size,
        zone.position,
        zone_footprint_size(zone.length_ft),
    )


def sync_persistent_beneficial_zones(setup: EncounterSetup, round_number: int) -> None:
    """Recompute zone-owned defenses from current source, zone, and member positions."""
    try:
        active = []
        for zone in setup.persistent_beneficial_zones:
            _remove_zone_effects(setup, zone.zone_id)
            source = _source_member(setup, zone.source_id)
            expired = round_number >= zone.expires_round
            ended = source is None or (
                zone.end_if_source_dead and source.state.is_dead
            ) or (
                zone.end_if_source_incapacitated and is_incapacitated(source.state)
            )
            if expired or ended:
                continue
            active.append(zone)

            for member in [*setup.heroes, *setup.monsters]:
                if member.side != zone.source_side or not _member_inside_zone(member, zone):
                    continue
                is_source = member.combatant_id == zone.source_id
                if not is_source or zone.include_source_for_defense:
                    if zone.armor_class_bonus:
                        add_modifier(member.state, CombatModifier(
                            id=f"{zone.zone_id}:{member.combatant_id}:ac",
                            source_id=zone.source_id,
                            source_effect_id=zone.zone_id,
                            source_name=zone.action_name,
                            source_is_magical=True,
                            kind=ModifierKind.ARMOR_CLASS,
                            flat_bonus=zone.armor_class_bonus,
                        ))
                    for ability in zone.saving_throw_abilities:
                        if zone.saving_throw_bonus:
                            add_modifier(member.state, CombatModifier(
                                id=f"{zone.zone_id}:{member.combatant_id}:save:{ability}",
                                source_id=zone.source_id,
                                source_effect_id=zone.zone_id,
                                source_name=zone.action_name,
                                source_is_magical=True,
                                kind=ModifierKind.SAVING_THROW_FLAT,
                                flat_bonus=zone.saving_throw_bonus,
                                save_ability=ability,
                            ))
                if not is_source and zone.ally_damage_resistances:
                    member.state.timed_effects.append(TimedEffect(
                        effect_id=f"{zone.zone_id}:{member.combatant_id}:resistance",
                        source_id=zone.source_id,
                        source_effect_id=zone.zone_id,
                        source_is_magical=True,
                        owned_damage_resistances=[
                            DamageType(item) for item in zone.ally_damage_resistances
                        ],
                    ))
        setup.persistent_beneficial_zones = active
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        logger.exception("Persistent beneficial zone synchronization failed.")
        raise RuntimeError("Persistent beneficial zone effects could not be synchronized.") from exc
