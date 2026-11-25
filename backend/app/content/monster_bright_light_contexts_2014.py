"""Source-proven 2014 bright-light reactions and permanent emitters."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.environment_contexts import (
    EmittedEnvironmentContext, EnvironmentContextControlAction, EnvironmentContextMode,
    EnvironmentContextReaction,
)

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

_MUTABLE_LIGHT_CLAUSES = {
    "Illumination": _normalized(
        "The flameskull sheds either dim light in a 15-foot radius, or bright light in a "
        "15-foot radius and dim light for an additional 15 feet. It can switch between "
        "the options as an action."
    ),
    "Ignited Illumination": _normalized(
        "As a bonus action, the magmin can set itself ablaze or extinguish its flames. "
        "While ablaze, the magmin sheds bright light in a 10-foot radius and dim light "
        "for an additional 10 feet."
    ),
    "Variable Illumination": _normalized(
        "The will-o'-wisp sheds bright light in a 5- to 20-foot radius and dim light for "
        "an additional number of feet equal to the chosen radius. The will-o'-wisp can "
        "alter the radius as a bonus action."
    ),
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


def mutable_bright_light_actions_2014(
    monster: SourceMonster2014,
) -> list[EnvironmentContextControlAction]:
    """Compile every exact source-declared mutable bright-light mode."""
    try:
        sections = source_sections_2014(monster.source_traits, include_continuations=True)
        actions: list[EnvironmentContextControlAction] = []
        if _normalized(sections.get("Illumination", "")) == _MUTABLE_LIGHT_CLAUSES["Illumination"]:
            actions.append(EnvironmentContextControlAction(
                id="illumination", name="Illumination", action_cost="action",
                initial_mode_id="bright-15", ai_mode_id="bright-15",
                modes=[
                    EnvironmentContextMode(id="dim-15"),
                    EnvironmentContextMode(id="bright-15", emitted_contexts=[
                        EmittedEnvironmentContext(context_id="bright_light", radius_ft=15),
                    ]),
                ],
            ))
        if _normalized(sections.get("Ignited Illumination", "")) == _MUTABLE_LIGHT_CLAUSES["Ignited Illumination"]:
            actions.append(EnvironmentContextControlAction(
                id="ignited-illumination", name="Ignited Illumination", action_cost="bonus_action",
                initial_mode_id="extinguished", ai_mode_id="ablaze",
                modes=[
                    EnvironmentContextMode(id="extinguished"),
                    EnvironmentContextMode(id="ablaze", emitted_contexts=[
                        EmittedEnvironmentContext(context_id="bright_light", radius_ft=10),
                    ]),
                ],
            ))
        if _normalized(sections.get("Variable Illumination", "")) == _MUTABLE_LIGHT_CLAUSES["Variable Illumination"]:
            actions.append(EnvironmentContextControlAction(
                id="variable-illumination", name="Variable Illumination", action_cost="bonus_action",
                initial_mode_id="bright-20", ai_mode_id="bright-20",
                modes=[EnvironmentContextMode(
                    id=f"bright-{radius}", emitted_contexts=[
                        EmittedEnvironmentContext(context_id="bright_light", radius_ft=radius),
                    ],
                ) for radius in range(5, 21)],
            ))
        return actions
    except Exception:
        logger.exception("2014 mutable bright-light source proof failed for %s.", monster.name)
        raise
