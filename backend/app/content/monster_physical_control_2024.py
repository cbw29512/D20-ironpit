from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

from app.domain.size import CreatureSize

_CONDITION_NAMES = (
    "Blinded|Charmed|Deafened|Frightened|Grappled|Incapacitated|Paralyzed|"
    "Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious"
)
_CONDITION_APPLICATION = re.compile(
    rf"\bhas the ((?:{_CONDITION_NAMES})(?:(?:, | and )(?:{_CONDITION_NAMES}))*) conditions?\b",
    re.I,
)
_ROLL_MARKER = re.compile(
    r"(?:Melee|Ranged|Melee or Ranged) Attack Roll:|"
    r"(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:",
    re.I,
)
_SAVE_MARKER = re.compile(
    r"(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*DC\s*(\d+)",
    re.I,
)
_SIZE = re.compile(
    r"(?:target is a|one)\s+(Tiny|Small|Medium|Large|Huge|Gargantuan)\s+or smaller creature",
    re.I,
)
_GRAPPLE = re.compile(r"\bhas the Grappled condition \(escape DC (\d+)\)", re.I)
_RESTRAINED_WITH_GRAPPLE = re.compile(
    r"\bhas the Restrained condition (?:until|while) the grapple ends\b|"
    r"\bWhile Grappled, the target has the Restrained condition\b",
    re.I,
)
_PRONE = re.compile(r"\bhas the Prone condition\b", re.I)
_FORCED_MOVEMENT = re.compile(
    r"\b(?:target is pushed|pushes the target|pulls? the target|pulled into|moves the target)\b",
    re.I,
)
_SWALLOW = re.compile(r"\bswallow(?:s|ed)?\b", re.I)
_UNSUPPORTED_GRAPPLE_DETAIL = re.compile(
    r"\bfrom (?:one of|both|all)\b|escape this grapple have Disadvantage",
    re.I,
)
_CHARGE_PRONE = re.compile(
    r"moved \d+\+? feet straight toward .* immediately before the hit",
    re.I,
)
_COMPLEX_SAVE_CONTROL = re.compile(
    r"\b(?:First Failure|Second Failure|repeats? the save|suffocat|"
    r"takes \d+ .* at the start|can't cast|can’t cast|moves with|destroyed|"
    r"Bonus Action to release)\b",
    re.I,
)
_PHYSICAL = {"grappled", "restrained", "prone"}


@dataclass(frozen=True)
class PhysicalControlBinding:
    action_name: str
    source_kind: str
    max_target_size: CreatureSize | None = None
    grapple_escape_dc: int | None = None
    restrains_while_grappled: bool = False
    knocks_prone: bool = False
    save_ability: str | None = None
    save_dc: int | None = None


def _action_name(actions: str, marker_start: int) -> str:
    prefix = actions[max(0, marker_start - 120):marker_start]
    match = re.search(r"([A-Z][A-Za-z’' -]+(?: \([^)]*\))?)\.\s*$", prefix)
    if match is None:
        raise ValueError(f"Could not identify action heading before {actions[marker_start:marker_start + 50]!r}.")
    return match.group(1).strip()


def _max_size(segment: str) -> CreatureSize | None:
    match = _SIZE.search(segment)
    return CreatureSize(match.group(1).lower()) if match else None


def _condition_counter(actions: str) -> Counter[str]:
    found: Counter[str] = Counter()
    for match in _CONDITION_APPLICATION.finditer(actions):
        for condition in re.findall(_CONDITION_NAMES, match.group(1), re.I):
            found[condition.lower()] += 1
    return found


def compile_physical_controls(row: dict[str, object]) -> list[PhysicalControlBinding]:
    actions = re.sub(r"\s+", " ", str(row.get("actions", ""))).strip()
    markers = list(_ROLL_MARKER.finditer(actions))
    compiled: list[PhysicalControlBinding] = []
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(actions)
        segment = actions[marker.start():end]
        if "Attack Roll:" in marker.group():
            if _UNSUPPORTED_GRAPPLE_DETAIL.search(segment):
                grapple = None
            else:
                grapple = _GRAPPLE.search(segment)
            prone = bool(_PRONE.search(segment) and not _CHARGE_PRONE.search(segment))
            if grapple or prone:
                compiled.append(PhysicalControlBinding(
                    action_name=_action_name(actions, marker.start()),
                    source_kind="attack",
                    max_target_size=_max_size(segment),
                    grapple_escape_dc=int(grapple.group(1)) if grapple else None,
                    restrains_while_grappled=bool(grapple and _RESTRAINED_WITH_GRAPPLE.search(segment)),
                    knocks_prone=prone,
                ))
            continue
        if _COMPLEX_SAVE_CONTROL.search(segment):
            continue
        save = _SAVE_MARKER.search(segment)
        if save is None or "Failure:" not in segment:
            continue
        grapple = _GRAPPLE.search(segment)
        prone = bool(_PRONE.search(segment))
        if grapple or prone:
            compiled.append(PhysicalControlBinding(
                action_name=_action_name(actions, marker.start()),
                source_kind="save",
                max_target_size=_max_size(segment),
                grapple_escape_dc=int(grapple.group(1)) if grapple else None,
                restrains_while_grappled=bool(grapple and _RESTRAINED_WITH_GRAPPLE.search(segment)),
                knocks_prone=prone,
                save_ability=save.group(1).lower(),
                save_dc=int(save.group(2)),
            ))
    return compiled


def compiled_condition_signatures(row: dict[str, object]) -> Counter[str]:
    result: Counter[str] = Counter()
    for binding in compile_physical_controls(row):
        if binding.grapple_escape_dc is not None:
            result["grappled"] += 1
            if binding.restrains_while_grappled:
                result["restrained"] += 1
        if binding.knocks_prone:
            result["prone"] += 1
    return result


def physical_control_coverage_matches(row: dict[str, object]) -> bool:
    actions = re.sub(r"\s+", " ", str(row.get("actions", ""))).strip()
    source = _condition_counter(actions)
    if any(condition not in _PHYSICAL for condition in source):
        return False
    if _FORCED_MOVEMENT.search(actions) or _SWALLOW.search(actions):
        return False
    return source == compiled_condition_signatures(row)
