from __future__ import annotations

from app.domain.capabilities import CombatantDefinition
from app.domain.traits import CombatTrait


def _merge_attacks(existing: CombatantDefinition, source: CombatantDefinition):
    source_by_id = {attack.id: attack for attack in source.attacks}
    merged = []
    for attack in existing.attacks:
        derived = source_by_id.get(attack.id)
        if derived is not None and attack.charge_profile is None and derived.charge_profile is not None:
            attack = attack.model_copy(update={"charge_profile": derived.charge_profile})
        merged.append(attack)
    return merged


def _merge_unique(existing: list, source: list) -> list:
    known = {item.id for item in existing}
    return [*existing, *(item for item in source if item.id not in known)]


def enrich_definition(existing: CombatantDefinition, source: CombatantDefinition) -> CombatantDefinition:
    attacks = _merge_attacks(existing, source)
    save_actions = _merge_unique(existing.save_actions, source.save_actions)
    resources = _merge_unique(existing.resources, source.resources)
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
