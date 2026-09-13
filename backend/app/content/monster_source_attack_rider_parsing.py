from __future__ import annotations

import re

from app.domain.capability_effects import ConditionEffectDefinition, HitSavingThrowEffectDefinition
from app.domain.size import CreatureSize
from app.domain.target_filters import TargetFilter

_CONDITIONS = "Blinded|Charmed|Deafened|Frightened|Incapacitated|Paralyzed|Petrified|Poisoned|Prone|Restrained|Stunned|Unconscious"
_CREATURE_TYPES = {
    "aberration", "beast", "celestial", "construct", "dragon", "elemental", "fey",
    "fiend", "giant", "humanoid", "monstrosity", "ooze", "plant", "undead",
}
SIZE_PATTERN = re.compile(r"\b(Tiny|Small|Medium|Large|Huge|Gargantuan)\s+or\s+smaller\b", re.I)
SAVE_CONDITION_PATTERN = re.compile(
    rf"(?:the\s+)?target[^.]{{0,240}}?must succeed on a DC\s*(?P<dc>\d+)\s*"
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw or "
    rf"(?:have|gain) the (?P<condition>{_CONDITIONS}) condition "
    rf"until the (?P<edge>start|end) of (?P<owner>its|the [^.]+?[’']s) next turn",
    re.I,
)
SAVE_FAILURE_CONDITION_PATTERN = re.compile(
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*DC\s*(?P<dc>\d+)[^.]*\.\s*"
    rf"Failure:\s*(?:The\s+)?target has the (?P<condition>{_CONDITIONS}) condition "
    rf"until the (?P<edge>start|end) of (?P<owner>its|the [^.]+?[’']s) next turn",
    re.I,
)
SEVERE_FAILURE_PATTERN = re.compile(
    rf"Failure by (?P<margin>\d+) or More:\s*The target has the (?P<condition>{_CONDITIONS}) condition "
    rf"for (?P<minutes>\d+) minute(?:s)?\.\s*While (?P=condition), the target has the "
    rf"(?P<linked>{_CONDITIONS}) condition, which ends early if the target takes any damage",
    re.I,
)
STAGED_SAVE_PATTERN = re.compile(
    rf"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*DC\s*(?P<dc>\d+)[^.]*\.\s*"
    rf"First Failure:\s*(?:The\s+)?target has the (?P<condition>{_CONDITIONS}) condition(?P<body>.*?)"
    rf"Second Failure:\s*(?:The\s+)?target has the (?P<second>{_CONDITIONS}) condition",
    re.I | re.S,
)


def maximum_target_size(text: str) -> CreatureSize | None:
    match = SIZE_PATTERN.search(text)
    return CreatureSize(match.group(1).lower()) if match else None


def target_filter(text: str) -> TargetFilter:
    excluded_types: set[str] = set()
    excluded_tags: set[str] = set()
    for match in re.finditer(r"\bnon-([A-Za-z]+)\s+creature\b", text, re.I):
        excluded_types.add(match.group(1).lower())
    match = re.search(r"\bisn[’']t\s+an?\s+([A-Za-z]+)(?:\s+or\s+([A-Za-z]+))?", text, re.I)
    if match:
        for value in (match.group(1), match.group(2)):
            if not value:
                continue
            normalized = value.lower()
            (excluded_types if normalized in _CREATURE_TYPES else excluded_tags).add(normalized)
    return TargetFilter(excluded_creature_types=sorted(excluded_types), excluded_tags=sorted(excluded_tags))


def _timing(owner: str, edge: str) -> str:
    actor = "target" if owner.lower() == "its" else "source"
    return f"{actor}_turn_{edge.lower()}"


def _staged_save(text: str, maximum: CreatureSize | None) -> HitSavingThrowEffectDefinition | None:
    match = STAGED_SAVE_PATTERN.search(text)
    if match is None:
        return None
    body = match.group("body").lower()
    if "repeats the save" not in body or "end of its next turn" not in body or "success" not in body:
        return None
    failure = ConditionEffectDefinition(
        condition=match.group("condition").lower(), max_target_size=maximum,
        repeat_save_ability=match.group("ability").lower(), repeat_save_dc=int(match.group("dc")),
        repeat_save_timing="target_turn_end", repeat_save_failure_condition=match.group("second").lower(),
    )
    return HitSavingThrowEffectDefinition(
        save_ability=match.group("ability").lower(), dc=int(match.group("dc")),
        target_filter=target_filter(text), failure_effects=[failure],
    )


def _severe_failure(text: str, maximum: CreatureSize | None) -> tuple[int, list[ConditionEffectDefinition]] | None:
    match = SEVERE_FAILURE_PATTERN.search(text)
    if match is None:
        return None
    duration = int(match.group("minutes")) * 10
    return int(match.group("margin")), [
        ConditionEffectDefinition(
            condition=match.group("condition").lower(), max_target_size=maximum,
            duration_rounds=duration, expiry_timing="source_turn_end",
        ),
        ConditionEffectDefinition(
            condition=match.group("linked").lower(), max_target_size=maximum,
            duration_rounds=duration, expiry_timing="source_turn_end", ends_on_damage=True,
        ),
    ]


def hit_save(text: str, maximum: CreatureSize | None) -> HitSavingThrowEffectDefinition | None:
    staged = _staged_save(text, maximum)
    if staged is not None:
        return staged
    match = SAVE_CONDITION_PATTERN.search(text) or SAVE_FAILURE_CONDITION_PATTERN.search(text)
    if match is None:
        return None
    failure = ConditionEffectDefinition(
        condition=match.group("condition").lower(), max_target_size=maximum,
        expiry_timing=_timing(match.group("owner"), match.group("edge")),
    )
    severe = _severe_failure(text, maximum)
    return HitSavingThrowEffectDefinition(
        save_ability=match.group("ability").lower(), dc=int(match.group("dc")),
        target_filter=target_filter(text), failure_effects=[failure],
        severe_failure_margin=severe[0] if severe else None,
        severe_failure_effects=severe[1] if severe else [],
    )


__all__ = ["hit_save", "maximum_target_size"]
