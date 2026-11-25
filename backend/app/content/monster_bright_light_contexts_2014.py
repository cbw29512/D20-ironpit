"""Source-proven 2014 bright-light reactions and permanent emitters."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.environment_contexts import EmittedEnvironmentContext, EnvironmentContextReaction

logger = logging.getLogger(__name__)


def _normalized(value: str) -> str:
    return " ".join(value.casefold().replace("\N{SOFT HYPHEN}", "").replace("’", "'").split())


_LIGHT_SENSITIVITY = _normalized(
    "While in bright light, the cloaker has disadvantage on attack rolls and "
    "Wisdom (Perception) checks that rely on sight."
)

# Complete clauses for unconditional fixed-radius sources. Mutable and variable
# light traits intentionally do not match; they require fight-state actions.
_PERMANENT_BRIGHT_LIGHT_CLAUSES = {
    _normalized("The azer sheds bright light in a 10-foot radius and dim light for an additional 10 feet."): 10,
    _normalized("The elemental sheds bright light in a 30-foot radius and dim light in an additional 30 feet."): 30,
    _normalized("The beetle sheds bright light in a 10-foot radius and dim light for an additional 10 feet."): 10,
    _normalized("The nightmare sheds bright light in a 10-foot radius and dim light for an additional 10 feet."): 10,
}


def light_sensitivity_reaction_2014(
    monster: SourceMonster2014,
) -> EnvironmentContextReaction | None:
    """Return the generic reaction only when the complete printed clause matches."""
    try:
        paragraphs = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).values()
        if _LIGHT_SENSITIVITY not in {_normalized(item) for item in paragraphs}:
            return None
        return EnvironmentContextReaction(
            source_id="light-sensitivity",
            source_name="Light Sensitivity",
            context_id="bright_light",
            disadvantage_on=["attack_rolls", "sight_based_perception_checks"],
        )
    except Exception:
        logger.exception("2014 Light Sensitivity source proof failed for %s.", monster.name)
        raise


def permanent_bright_light_contexts_2014(
    monster: SourceMonster2014,
) -> list[EmittedEnvironmentContext]:
    """Compile every exact fixed-radius bright-light clause on the immutable card."""
    try:
        contexts: list[EmittedEnvironmentContext] = []
        for paragraph in source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).values():
            radius = _PERMANENT_BRIGHT_LIGHT_CLAUSES.get(_normalized(paragraph))
            if radius is not None:
                contexts.append(EmittedEnvironmentContext(
                    context_id="bright_light", radius_ft=radius,
                ))
        return contexts
    except Exception:
        logger.exception("2014 permanent bright-light source proof failed for %s.", monster.name)
        raise
