from __future__ import annotations

import logging

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def replacement_form_source_template(ruleset: str, template_id: str) -> CombatantTemplate:
    """Resolve a replacement-form source from the certified ruleset roster."""
    try:
        if ruleset != "2014":
            raise ValueError(f"Replacement-form source registry does not yet support ruleset {ruleset}.")
        from app.content.monster_roster_2014 import build_basic_2014_monsters

        by_id = {template.id: template for template in build_basic_2014_monsters()}
        template = by_id.get(template_id)
        if template is None:
            raise ValueError(f"Replacement-form source {template_id} is not certified for {ruleset}.")
        return template.model_copy(deep=True)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve replacement-form source %s for %s.", template_id, ruleset)
        raise RuntimeError("Replacement-form source could not be resolved.") from exc
