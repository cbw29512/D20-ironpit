from __future__ import annotations

import re

from app.domain.capability_effects import GrappleEffectDefinition, ProneEffectDefinition
from app.domain.save_effects import ConditionEffectDefinition, TurnRestrictionEffectDefinition
from app.domain.size import CreatureSize

_SIZE = re.compile(r"\b(Tiny|Small|Medium|Large|Huge|Gargantuan)\s+or\s+smaller\b", re.I)
_PUSH = re.compile(r"pushed\s+up\s+to\s+(\d+)\s+feet\s+straight\s+away", re.I)
_GRAPPLE = re.compile(r"Grappled condition\s*\(escape DC\s*(\d+)\)", re.I)
_TIMED_CONDITION = re.compile(
    r"has the (Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Poisoned|Prone|Restrained|Stunned|Unconscious) condition "
    r"until the (start|end) of (?:its|the [^.]+?['’]s) next turn", re.I,
)


def target_max_size(target_text: str) -> CreatureSize | None:
    match = _SIZE.search(target_text)
    return CreatureSize(match.group(1).lower()) if match else None


def common_failure_riders(target_text: str, failure_text: str) -> dict[str, object]:
    result: dict[str, object] = {"failure_effects": []}
    maximum = target_max_size(target_text)
    effects: list[object] = result["failure_effects"]  # type: ignore[assignment]
    push = _PUSH.search(failure_text)
    if push:
        result["push_target_away_ft"] = int(push.group(1))
        result["push_target_max_size"] = maximum
    if re.search(r"\bProne condition\b", failure_text, re.I):
        effects.append(ProneEffectDefinition(max_target_size=maximum))
    grapple = _GRAPPLE.search(failure_text)
    if grapple:
        result["grapple"] = GrappleEffectDefinition(
            escape_dc=int(grapple.group(1)), max_target_size=maximum,
            restrains=bool(re.search(r"Restrained condition.*until the grapple ends", failure_text, re.I)),
        )
    timed = _TIMED_CONDITION.search(failure_text)
    if timed and timed.group(1).lower() != "prone":
        timing = f"target_turn_{timed.group(2).lower()}"
        effects.append(ConditionEffectDefinition(condition=timed.group(1).lower(), expiry_timing=timing))
    return result


def slowing_breath_rider(failure_text: str) -> TurnRestrictionEffectDefinition | None:
    clauses = failure_text.lower()
    if not all(fragment in clauses for fragment in ("can’t take reactions", "speed is halved", "action or a bonus action")):
        return None
    if "until the end of its next turn" not in clauses and "lasts until the end of its next turn" not in clauses:
        return None
    return TurnRestrictionEffectDefinition(
        action_or_bonus_only=True, reactions_disabled=True, speed_multiplier=0.5,
        expiry_timing="target_turn_end",
    )
