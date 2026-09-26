from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CanonicalWildShapeForm:
    min_level: int
    max_level: int
    monster_id: str
    name: str
    challenge_rating: str


_FORMS = (
    CanonicalWildShapeForm(2, 3, "2014-wolf", "Wolf", "1/4"),
    CanonicalWildShapeForm(4, 7, "2014-crocodile", "Crocodile", "1/2"),
    CanonicalWildShapeForm(8, 20, "2014-brown-bear", "Brown Bear", "1"),
)


def canonical_wild_shape_form_2014(level: int) -> CanonicalWildShapeForm:
    try:
        if level not in range(2, 21):
            raise ValueError("2014 Land Druid Wild Shape forms cover levels 2 through 20.")
        for form in _FORMS:
            if form.min_level <= level <= form.max_level:
                return form
        raise ValueError(f"No canonical 2014 Wild Shape form defined for level {level}.")
    except Exception:
        logger.exception("Failed to resolve canonical 2014 Wild Shape form for level %s.", level)
        raise


def canonical_wild_shape_template_2014(level: int):
    try:
        from app.content.monster_roster_2014 import build_basic_2014_monsters

        form = canonical_wild_shape_form_2014(level)
        by_id = {template.id: template for template in build_basic_2014_monsters()}
        template = by_id.get(form.monster_id)
        if template is None:
            raise ValueError(
                f"Canonical 2014 Wild Shape form {form.monster_id} is not in the certified 2014 monster roster."
            )
        if template.challenge_rating != form.challenge_rating:
            raise ValueError(
                f"Canonical Wild Shape form CR drift for {form.monster_id}: "
                f"{template.challenge_rating} != {form.challenge_rating}."
            )
        return template.model_copy(deep=True)
    except Exception:
        logger.exception("Failed to compile canonical 2014 Wild Shape template for level %s.", level)
        raise
