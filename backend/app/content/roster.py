from __future__ import annotations

import logging

from app.content.capability_registry import build_monster_templates_from_capabilities
from app.content.certified_heroes import build_certified_hero_templates_for_ruleset
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_unarmed_2014 import complete_2014_monster_unarmed_profiles
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles
from app.domain.models import ArenaRoster
from app.domain.rulesets import DEFAULT_RULESET, RulesetId

logger = logging.getLogger(__name__)


def build_arena_roster(ruleset: RulesetId = DEFAULT_RULESET) -> ArenaRoster:
    try:
        characters = complete_unarmed_opportunity_profiles(
            build_certified_hero_templates_for_ruleset(ruleset)
        )
        if ruleset == "2014":
            monsters = complete_2014_monster_unarmed_profiles(build_basic_2014_monsters())
        elif ruleset == "2024":
            monsters = build_monster_templates_from_capabilities()
        else:
            raise ValueError(f"Unsupported ruleset: {ruleset}.")
        templates = [*characters, *monsters]
        if not templates or {template.ruleset for template in templates} != {ruleset}:
            raise ValueError(f"Ruleset {ruleset} roster crossed the edition boundary.")
        return ArenaRoster(characters=characters, monsters=list(monsters))
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to build Iron Pit %s arena roster.", ruleset)
        raise RuntimeError(f"Iron Pit {ruleset} arena roster could not be created.") from exc
