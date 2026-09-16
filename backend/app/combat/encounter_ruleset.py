from __future__ import annotations

import logging

from app.domain.combatants import CombatantTemplate
from app.domain.rulesets import RulesetId

logger = logging.getLogger(__name__)


def resolve_encounter_ruleset(templates: list[CombatantTemplate]) -> RulesetId:
    try:
        rulesets = {template.ruleset for template in templates}
        if not rulesets:
            raise ValueError("Encounter requires at least one combatant ruleset.")
        if len(rulesets) != 1:
            joined = ", ".join(sorted(rulesets))
            raise ValueError(f"Mixed rulesets are not allowed in one Iron Pit fight: {joined}.")
        return next(iter(rulesets))
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve encounter ruleset.")
        raise RuntimeError("Encounter ruleset could not be resolved.") from exc
