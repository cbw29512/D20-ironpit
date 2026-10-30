from __future__ import annotations

import logging
import re

from app.domain.capability_effects import ConditionEffectDefinition
from app.domain.hit_modifiers import CombatModifierEffect
from app.domain.size import CreatureSize

logger = logging.getLogger(__name__)
_CONDITION = re.compile(
    r"target has the (Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious) condition",
    re.IGNORECASE,
)
_SOURCE_TURN_CONDITION = re.compile(
    r"target has the (?P<condition>Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious) condition "
    r"until the (?P<edge>start|end) of the [^.]+?[’']s next turn",
    re.IGNORECASE,
)
_HEALING_PREVENTED = re.compile(r"(?:can[’']t|cannot) regain Hit Points", re.IGNORECASE)


def timed_attack_riders(
    text: str,
    maximum: CreatureSize | None,
    failed_condition: str | None,
    grapple_present: bool,
) -> list[object]:
    """Compile source-owned timed conditions and lifecycle-linked healing prevention."""
    try:
        condition = _CONDITION.search(text)
        if condition is None:
            return []
        name = condition.group(1).lower()
        if name in {"prone", failed_condition} or grapple_present:
            return []

        timed = _SOURCE_TURN_CONDITION.search(text)
        expiry = (
            f"source_turn_{timed.group('edge').lower()}"
            if timed and timed.group("condition").lower() == name
            else None
        )
        effects: list[object] = [
            ConditionEffectDefinition(
                condition=name,
                max_target_size=maximum,
                expiry_timing=expiry,
            )
        ]
        if _HEALING_PREVENTED.search(text):
            if expiry not in {"source_turn_start", "source_turn_end"}:
                raise ValueError("Healing-prevention rider requires a finite source-owned duration.")
            effects.append(CombatModifierEffect(
                kind="healing-prevented",
                expires_at_start_of_source_turn=expiry == "source_turn_start",
                expires_at_end_of_source_turn=expiry == "source_turn_end",
            ))
        return effects
    except (TypeError, ValueError):
        logger.exception("Invalid timed attack rider source text.")
        raise
    except Exception as exc:
        logger.exception("Timed attack rider parsing failed.")
        raise RuntimeError("Timed attack riders could not be parsed.") from exc
