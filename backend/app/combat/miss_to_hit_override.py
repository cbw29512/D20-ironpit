from __future__ import annotations

import logging

from app.domain.models import CombatantState

logger = logging.getLogger(__name__)


def _consume_grant(attacker: CombatantState, grant: object) -> bool:
    """Consume the configured usage window without knowing the source ability identity."""
    try:
        usage_policy = grant.usage_policy
        if usage_policy == "resource":
            resource_id = grant.resource_id
            if resource_id is None:
                raise ValueError(f"Resource-backed miss-to-hit override {grant.source_id} has no resource_id.")
            resource = next((item for item in attacker.resources if item.id == resource_id), None)
            if resource is None:
                raise ValueError(f"Miss-to-hit override {grant.source_id} references missing resource {resource_id}.")
            if resource.current_uses <= 0:
                return False
            resource.current_uses -= 1
            return True
        if usage_policy == "refresh_at_turn_start":
            if grant.source_id in attacker.turn_start_feature_cooldowns:
                return False
            attacker.turn_start_feature_cooldowns.append(grant.source_id)
            return True
        raise ValueError(f"Unsupported miss-to-hit usage policy: {usage_policy}.")
    except Exception as exc:
        logger.exception("Failed to consume miss-to-hit usage for %s.", attacker.template.name)
        raise RuntimeError("Miss-to-hit usage could not be consumed.") from exc


def apply_miss_to_hit_override(
    attacker: CombatantState,
    *,
    hit: bool,
) -> tuple[bool, str | None, str | None]:
    """Convert a miss to a normal hit through one universal declarative capability."""
    try:
        if hit:
            return True, None, None

        for grant in attacker.template.progression_features.miss_to_hit_override_grants:
            if _consume_grant(attacker, grant):
                return True, grant.source_id, grant.source_name

        # Transitional compatibility for already-certified source data.
        resource_id = attacker.template.progression_features.miss_to_hit_override_resource_id
        if resource_id is None:
            return False, None, None
        resource = next((item for item in attacker.resources if item.id == resource_id), None)
        if resource is None:
            raise ValueError(f"Miss-to-hit override references missing resource {resource_id}.")
        if resource.current_uses <= 0:
            return False, None, None
        resource.current_uses -= 1
        definition = next((item for item in attacker.template.resources if item.id == resource_id), None)
        source_name = (
            attacker.template.progression_features.miss_to_hit_override_source_name
            or (definition.name if definition is not None else resource_id)
        )
        return True, resource_id, source_name
    except Exception as exc:
        logger.exception("Failed to resolve miss-to-hit override for %s.", attacker.template.name)
        raise RuntimeError("Miss-to-hit override could not be resolved.") from exc
