from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.combatants import ResourceDefinition
from app.domain.zero_hp_effects import DamageThresholdZeroHpReplacement

logger = logging.getLogger(__name__)


def _source_trait_name(monster: SourceMonster2014, resource_id: str) -> str:
    matches = [
        name for name in monster.trait_names
        if name.casefold().startswith(resource_id.casefold())
    ]
    if len(matches) != 1:
        raise ValueError(
            f"{monster.name} zero-HP prevention resource {resource_id!r} must map "
            f"to exactly one printed trait heading; found {matches!r}."
        )
    return matches[0]


def damage_threshold_zero_hp_replacements_2014(
    monster: SourceMonster2014,
) -> list[DamageThresholdZeroHpReplacement]:
    """Compile parsed 2014 thresholded zero-HP prevention into a universal rule."""
    try:
        payload = monster.zero_hp_prevention
        if payload is None:
            return []
        if not isinstance(payload, dict):
            raise ValueError(f"{monster.name} zero_hp_prevention must be an object.")
        expected = {"resource_id", "max_trigger_damage", "resulting_hp"}
        if set(payload) != expected:
            raise ValueError(
                f"{monster.name} zero_hp_prevention fields drifted: "
                f"{sorted(payload)} != {sorted(expected)}."
            )
        resource_id = str(payload["resource_id"]).strip()
        if not resource_id:
            raise ValueError(f"{monster.name} zero-HP prevention resource id is empty.")
        max_trigger_damage = int(payload["max_trigger_damage"])
        resulting_hp = int(payload["resulting_hp"])
        if max_trigger_damage < 0 or resulting_hp < 1:
            raise ValueError(
                f"{monster.name} has invalid zero-HP prevention payload {payload!r}."
            )
        source_name = _source_trait_name(monster, resource_id)
        return [DamageThresholdZeroHpReplacement(
            source_id=f"2014-{monster.id}-{resource_id}",
            source_name=source_name,
            resource_id=resource_id,
            resource_cost=1,
            max_trigger_damage=max_trigger_damage,
            replacement_hp=resulting_hp,
        )]
    except Exception:
        logger.exception("Failed to bind 2014 zero-HP prevention for %s.", monster.name)
        raise


def zero_hp_prevention_resources_2014(
    monster: SourceMonster2014,
) -> list[ResourceDefinition]:
    try:
        return [
            ResourceDefinition(id=rule.resource_id, name=rule.source_name, max_uses=1)
            for rule in damage_threshold_zero_hp_replacements_2014(monster)
        ]
    except Exception:
        logger.exception("Failed to build 2014 zero-HP resources for %s.", monster.name)
        raise


def bound_zero_hp_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    return frozenset(
        rule.source_name for rule in damage_threshold_zero_hp_replacements_2014(monster)
    )


def supports_zero_hp_prevention_2014(monster: SourceMonster2014) -> bool:
    return bool(damage_threshold_zero_hp_replacements_2014(monster))
