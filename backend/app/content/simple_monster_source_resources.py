from __future__ import annotations

import re

from app.content.monster_combat_scope import base_feature_name
from app.content.monster_limited_use_source import limited_use_spec, parse_limited_use_names


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _bind(entry: dict[str, object], resource_id: str) -> None:
    existing = entry.get("resource_id")
    if existing is not None and existing != resource_id:
        raise ValueError(f"Capability {entry.get('id')!r} already uses resource {existing!r}.")
    entry["resource_id"] = resource_id
    entry["resource_cost"] = 1


def attach_limited_use_resources(
    row: dict[str, object],
    attacks: list[dict[str, object]],
    save_actions: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[str]]:
    """Bind parseable Recharge/N-per-Day actions to the shared finite-resource model."""
    fingerprints = parse_limited_use_names(row)
    monster_slug = _slug(str(row["name"])); resources: list[dict[str, object]] = []
    for fingerprint in fingerprints:
        spec = limited_use_spec(fingerprint)
        matching_attacks = [
            attack for attack in attacks
            if spec.section == "actions" and base_feature_name(str(attack["name"])) == spec.base_name
        ]
        expected_cost = "bonus_action" if spec.section == "bonusActions" else "action"
        matching_saves = [
            action for action in save_actions
            if spec.section in {"actions", "bonusActions"}
            and base_feature_name(str(action["name"])) == spec.base_name
            and str(action.get("action_cost", "action")) == expected_cost
        ]
        if not matching_attacks and not matching_saves:
            continue
        resource_id = f"srd-{monster_slug}-{_slug(spec.section)}-{_slug(spec.base_name)}-uses"
        for capability in [*matching_attacks, *matching_saves]:
            _bind(capability, resource_id)
        resource: dict[str, object] = {
            "id": resource_id,
            "name": spec.base_name,
            "max_uses": spec.max_uses,
        }
        if spec.recharge_minimum is not None:
            resource["recharge"] = {
                "minimum": spec.recharge_minimum,
                "maximum": spec.recharge_maximum,
                "die_size": 6,
            }
        resources.append(resource)
    return resources, fingerprints
