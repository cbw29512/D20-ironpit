from __future__ import annotations

import logging

from app.content.certified_heroes import build_certified_hero_templates_for_ruleset
from app.content.ruleset_monster_rosters import build_monster_templates_for_ruleset
from app.content.unarmed_opportunity_profiles import complete_unarmed_opportunity_profiles
from app.domain.models import ArenaRoster
from app.domain.rulesets import DEFAULT_RULESET, RulesetId

logger = logging.getLogger(__name__)


def build_arena_roster(ruleset: RulesetId = DEFAULT_RULESET) -> ArenaRoster:
    try:
        characters = complete_unarmed_opportunity_profiles(
            build_certified_hero_templates_for_ruleset(ruleset)
        )
        monsters = build_monster_templates_for_ruleset(ruleset)
        templates = [*characters, *monsters]
        if not templates or {template.ruleset for template in templates} != {ruleset}:
            raise ValueError(f"Ruleset {ruleset} roster crossed the edition boundary.")
        return ArenaRoster(characters=characters, monsters=list(monsters))
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to build Iron Pit %s arena roster.", ruleset)
        raise RuntimeError(f"Iron Pit {ruleset} arena roster could not be created.") from exc
