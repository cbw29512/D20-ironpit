from __future__ import annotations

import logging
import re

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_DAILY_FINGERPRINT = re.compile(
    r"^(?P<section>[^:]+):(?P<name>.+?)\s+\((?P<uses>\d+)\s*/\s*Day\)$",
    re.IGNORECASE,
)
_ACTION_COST_SECTION = {
    "action": "actions",
    "bonus_action": "bonusactions",
    "reaction": "reactions",
}


def _normalized_name(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    except Exception:
        logger.exception("Failed to normalize limited-use action name %r.", value)
        raise


def _resource_action_bindings(template: CombatantTemplate) -> list[tuple[str, int, str, str]]:
    try:
        rows: list[tuple[str, int, str, str]] = []
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]:
            if attack.resource_id:
                rows.append((attack.resource_id, attack.resource_cost, attack.weapon.name, "actions"))
        for action in template.saving_throw_actions:
            if action.resource_id:
                section = _ACTION_COST_SECTION.get(action.action_cost)
                if section is not None:
                    rows.append((action.resource_id, action.resource_cost, action.name, section))
        for feature in template.triggered_bonus_attacks:
            rows.append((feature.resource_id, feature.resource_cost, feature.name, "bonusactions"))
        for action in [
            *template.spell_attack_actions,
            *template.spell_save_actions,
            *template.defensive_spell_actions,
            *template.healing_actions,
        ]:
            if action.resource_id:
                section = _ACTION_COST_SECTION.get(action.action_cost)
                if section is not None:
                    rows.append((action.resource_id, action.resource_cost, action.name, section))
        return rows
    except Exception:
        logger.exception("Failed to collect daily-use action bindings for %s.", template.name)
        raise


def daily_fingerprint_implemented(template: CombatantTemplate, fingerprint: str) -> bool:
    try:
        match = _DAILY_FINGERPRINT.fullmatch(fingerprint.strip())
        if match is None:
            return False
        section = match.group("section").lower()
        if section not in set(_ACTION_COST_SECTION.values()):
            return False
        source_name = _normalized_name(match.group("name"))
        uses = int(match.group("uses"))
        bindings = _resource_action_bindings(template)
        return any(
            definition.max_uses == uses
            and definition.recharge is None
            and _normalized_name(definition.name) == source_name
            and any(
                resource_id == definition.id
                and cost == 1
                and _normalized_name(action_name) == source_name
                and action_section == section
                for resource_id, cost, action_name, action_section in bindings
            )
            for definition in template.resources
        )
    except Exception:
        logger.exception("Failed to audit daily-use fingerprint %r for %s.", fingerprint, template.name)
        raise
