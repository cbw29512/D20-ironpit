from __future__ import annotations

import logging

from app.content.capability_registry import build_monster_templates_from_capabilities
from app.content.certified_heroes import build_certified_hero_templates
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles
from app.domain.models import ArenaRoster
from app.domain.rulesets import DEFAULT_RULESET, RulesetId

logger = logging.getLogger(__name__)


def build_arena_roster(ruleset: RulesetId = DEFAULT_RULESET) -> ArenaRoster:
    try:
        if ruleset != "2024":
            raise ValueError(f"Ruleset {ruleset} roster is not admitted for combat yet.")
        characters = complete_unarmed_opportunity_profiles(build_certified_hero_templates())
        return ArenaRoster(
            characters=characters,
            monsters=build_monster_templates_from_capabilities(),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to build Iron Pit %s arena roster.", ruleset)
        raise RuntimeError(f"Iron Pit {ruleset} arena roster could not be created.") from exc
