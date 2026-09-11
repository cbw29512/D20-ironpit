from __future__ import annotations

import re

from app.domain.capabilities import CombatantDefinition
from app.domain.traits import CombatTrait


def _normalized_name(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def _merge_attacks(existing: CombatantDefinition, source: CombatantDefinition):
    source_by_id = {attack.id: attack for attack in source.attacks}
    merged = []
    for attack in existing.attacks:
        derived = source_by_id.get(attack.id)
        if derived is not None and attack.charge_profile is None and derived.charge_profile is not None:
            attack = attack.model_copy(update={"charge_profile": derived.charge_profile})
        merged.append(attack)
    return merged


def _resource_rebinds(existing: list, source: list) -> dict[str, str]:
    by_id = {item.id: item for item in existing}
    by_name = {_normalized_name(item.name): item for item in existing}
    rebinds: dict[str, str] = {}
    for item in source:
        canonical = by_id.get(item.id) or by_name.get(_normalized_name(item.name))
        if canonical is not None:
            rebinds[item.id] = canonical.id
    return rebinds


def _merge_resources(existing: list, source: list) -> list:
    known_ids = {item.id for item in existing}
    known_names = {_normalized_name(item.name) for item in existing}
    additions = [
        item for item in source
        if item.id not in known_ids and _normalized_name(item.name) not in known_names
    ]
    return [*existing, *additions]


def _save_key(action: object) -> tuple[str, str]:
    return (_normalized_name(action.name), action.action_cost)


def _merge_save_actions(existing: list, source: list, resource_rebinds: dict[str, str]) -> list:
    source_by_key = {_save_key(action): action for action in source}
    existing_keys = {_save_key(action) for action in existing}
    merged = []
    for current in existing:
        derived = source_by_key.get(_save_key(current))
        if derived is None:
            merged.append(current)
            continue
        resource_id = derived.resource_id
        if resource_id is not None:
            resource_id = resource_rebinds.get(resource_id, resource_id)
        merged.append(derived.model_copy(update={
            "id": current.id,
            "resource_id": current.resource_id or resource_id,
        }))
    for derived in source:
        if _save_key(derived) in existing_keys:
            continue
        resource_id = derived.resource_id
        if resource_id is not None:
            resource_id = resource_rebinds.get(resource_id, resource_id)
        merged.append(derived.model_copy(update={"resource_id": resource_id}))
    return merged


def enrich_definition(existing: CombatantDefinition, source: CombatantDefinition) -> CombatantDefinition:
    attacks = _merge_attacks(existing, source)
    resource_rebinds = _resource_rebinds(existing.resources, source.resources)
    save_actions = _merge_save_actions(existing.save_actions, source.save_actions, resource_rebinds)
    resources = _merge_resources(existing.resources, source.resources)
    traits = list(dict.fromkeys([*existing.combat_traits, *source.combat_traits]))
    if any(attack.charge_profile is not None for attack in attacks) and CombatTrait.CHARGE not in traits:
        traits.append(CombatTrait.CHARGE)
    return existing.model_copy(update={
        "attacks": attacks,
        "save_actions": save_actions,
        "resources": resources,
        "combat_traits": traits,
    })


def enrich_registry(
    existing: dict[str, CombatantDefinition], source: dict[str, CombatantDefinition],
) -> dict[str, CombatantDefinition]:
    merged = dict(existing)
    for combatant_id, source_definition in source.items():
        current = merged.get(combatant_id)
        merged[combatant_id] = source_definition if current is None else enrich_definition(current, source_definition)
    return merged
