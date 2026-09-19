from __future__ import annotations

import logging

from app.content.capability_registry import build_monster_templates_from_capabilities
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_unarmed_2014 import complete_2014_monster_unarmed_profiles
from app.domain.models import CombatantTemplate
from app.domain.rulesets import RulesetId

logger = logging.getLogger(__name__)


def build_monster_templates_for_ruleset(ruleset: RulesetId) -> list[CombatantTemplate]:
    """Return the certified monster roster for one explicit ruleset."""
    try:
        if ruleset == "2014":
            return complete_2014_monster_unarmed_profiles(build_basic_2014_monsters())
        if ruleset == "2024":
            return build_monster_templates_from_capabilities()
        raise ValueError(f"Unsupported ruleset: {ruleset}.")
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to build %s certified monster roster.", ruleset)
        raise RuntimeError(f"Certified {ruleset} monster roster could not be built.") from exc
