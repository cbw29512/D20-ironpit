from __future__ import annotations

from fractions import Fraction
import logging

from app.domain.models import CombatantTemplate
from app.domain.unarmed import UnarmedStrikeDamage

logger = logging.getLogger(__name__)


def proficiency_bonus_from_cr_2014(challenge_rating: str | None) -> int:
    """Return the 2014 monster proficiency bonus implied by Challenge Rating."""
    if challenge_rating is None:
        raise ValueError("2014 monster requires Challenge Rating for Unarmed Strike proficiency.")
    value = Fraction(challenge_rating)
    if value < 0 or value > 30:
        raise ValueError(f"Unsupported 2014 Challenge Rating: {challenge_rating!r}.")
    if value < 5:
        return 2
    return 2 + (int(value) - 1) // 4


def complete_2014_monster_unarmed_profiles(
    templates: tuple[CombatantTemplate, ...] | list[CombatantTemplate],
) -> list[CombatantTemplate]:
    """Attach 2014 Unarmed Strike fallback profiles without consulting 2024 source rows."""
    try:
        completed: list[CombatantTemplate] = []
        for template in templates:
            if template.ruleset != "2014" or template.kind != "monster":
                raise ValueError("2014 monster Unarmed Strike completion received a cross-edition template.")
            scores = template.ability_scores
            if scores is None:
                raise ValueError(f"{template.name} lacks source-derived ability scores.")
            modifier = scores.modifier("strength")
            profile = UnarmedStrikeDamage(
                attack_bonus=modifier + proficiency_bonus_from_cr_2014(template.challenge_rating),
                damage=max(0, 1 + modifier),
            )
            completed.append(template.model_copy(update={"unarmed_opportunity_attack": profile}))
        return completed
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to complete 2014 monster Unarmed Strike profiles.")
        raise RuntimeError("2014 monster Unarmed Strike profiles could not be completed.") from exc
