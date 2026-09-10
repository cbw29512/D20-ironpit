from __future__ import annotations

import logging
import re

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_RECHARGE_FINGERPRINT = re.compile(
    r"^(?P<section>[^:]+):(?P<name>.+?)\s+\(Recharge\s+(?P<minimum>\d)(?:\s*[-–]\s*(?P<maximum>\d))?\)$",
    re.IGNORECASE,
)


def _normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _resource_bound_actions(template: CombatantTemplate) -> list[tuple[str, int, str]]:
    """Enumerate every action family using the universal resource contract."""
    bindings: list[tuple[str, int, str]] = []
    for attack in [template.weapon_attack, *template.alternate_weapon_attacks]:
        if attack.resource_id:
            bindings.append((attack.resource_id, attack.resource_cost, attack.weapon.name))
    for action in template.saving_throw_actions:
        if action.resource_id:
            bindings.append((action.resource_id, action.resource_cost, action.name))
    for action in [
        *template.spell_attack_actions,
        *template.spell_save_actions,
        *template.defensive_spell_actions,
        *template.healing_actions,
    ]:
        if action.resource_id:
            bindings.append((action.resource_id, action.resource_cost, action.name))
    return bindings


def recharge_fingerprint_implemented(template: CombatantTemplate, fingerprint: str) -> bool:
    """Return True only when a source Recharge action is bound to matching runtime economy."""
    try:
        match = _RECHARGE_FINGERPRINT.fullmatch(fingerprint.strip())
        if match is None or match.group("section").lower() != "actions":
            return False
        minimum = int(match.group("minimum"))
        maximum = int(match.group("maximum") or match.group("minimum"))
        if maximum != 6:
            return False
        source_name = _normalized_name(match.group("name"))
        bindings = _resource_bound_actions(template)
        for definition in template.resources:
            rule = definition.recharge
            if rule is None or definition.max_uses != 1:
                continue
            if rule.trigger != "start_of_turn" or rule.die_size != 6 or rule.minimum_roll != minimum:
                continue
            if _normalized_name(definition.name) != source_name:
                continue
            if any(
                resource_id == definition.id
                and cost == 1
                and _normalized_name(action_name) == source_name
                for resource_id, cost, action_name in bindings
            ):
                return True
        return False
    except Exception:
        logger.exception("Failed to audit Recharge fingerprint %r for %s.", fingerprint, template.name)
        raise
