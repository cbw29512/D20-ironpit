from __future__ import annotations

import logging
import re

from app.domain.actions import ActionCost
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import ConditionEffectDefinition

logger = logging.getLogger(__name__)

_CONDITION = (
    r"Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Poisoned|"
    r"Prone|Restrained|Stunned|Unconscious|Petrified"
)
_REPEAT_CONDITION_SAVE = re.compile(
    rf"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+"
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s+"
    rf"DC\s+(?P<dc>\d+),\s+(?P<target>[^.]+)\.\s+"
    rf"Failure:\s+The target has the (?P<condition>{_CONDITION}) condition and repeats the save "
    rf"at the end of each of its turns, ending the effect on itself on a success\.\s+"
    rf"After (?P<minutes>\d+) minute(?:s)?, it succeeds automatically\.\s+"
    rf"While (?P=condition), the target has the (?P<linked>{_CONDITION}) condition\.",
    re.I,
)
_REACH = re.compile(r"reach\s+(\d+)\s*ft\.", re.I)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _range_ft(text: str, match: re.Match[str]) -> int:
    target = match.group("target")
    within = re.search(r"within\s+(\d+)\s+feet", target, re.I)
    if within:
        return int(within.group(1))
    if re.search(r"Grappled by the\s+", target, re.I):
        reaches = [int(value) for value in _REACH.findall(text[:match.start()])]
        return max(reaches, default=5)
    return 5


def repeat_condition_save_candidates(
    monster: str,
    text: str,
    action_cost: ActionCost,
) -> list[SaveCapabilityDefinition]:
    """Compile repeating failed-save conditions that carry a linked condition."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        for match in _REPEAT_CONDITION_SAVE.finditer(text):
            condition = match.group("condition").lower()
            target = match.group("target")
            effect = ConditionEffectDefinition(
                condition=condition,
                linked_conditions=[match.group("linked").lower()],
                repeat_save_ability=match.group("ability").lower(),
                repeat_save_dc=int(match.group("dc")),
                repeat_save_timing="target_turn_end",
                automatic_success_after_rounds=int(match.group("minutes")) * 10,
            )
            actions.append(SaveCapabilityDefinition(
                id=f"srd-{_slug(monster)}-{_slug(match.group('name'))}",
                name=match.group("name").strip(),
                action_cost=action_cost,
                save_ability=match.group("ability").lower(),
                dc=int(match.group("dc")),
                range_ft=_range_ft(text, match),
                required_target_grappled_by_self=bool(re.search(r"Grappled by the\s+", target, re.I)),
                failure_effects=[effect],
                animation="save-effect",
            ))
        return actions
    except (TypeError, ValueError):
        logger.exception("Invalid repeat-save source data for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Repeat-save parsing failed for %s.", monster)
        raise RuntimeError(f"Repeat-save parsing failed for {monster}.") from exc
