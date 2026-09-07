from __future__ import annotations

import re
from collections.abc import Iterable

from app.domain.models import WeaponAttack

_HP_MAX_REDUCTION = re.compile(
    r"\bHit Point maximum\s+(?:decreases|is reduced)\b",
    re.IGNORECASE,
)
_TYPED_HP_MAX_REDUCTION = re.compile(
    r"\bHit Point maximum\s+(?:decreases|is reduced)[^.]{0,120}?equal to (?:the )?"
    r"(Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder) damage taken",
    re.IGNORECASE,
)
_COMBATANT_CREATION = re.compile(
    r"\b(?:summons?|creates?)\b[^.]{0,100}\b(?:creature|monster|specter|zombie|skeleton)\b"
    r"|\brises(?!\s+\d+\s+hours?\s+later)\s+as\s+(?:a|an)\s+[A-Za-z’'\-]+\b",
    re.IGNORECASE,
)


def _modeled_max_hp_riders(attacks: Iterable[WeaponAttack]) -> list[WeaponAttack]:
    return [attack for attack in attacks if attack.max_hp_reduction is not None]


def survival_action_issues(actions: object, runtime_attacks: Iterable[WeaponAttack] = ()) -> list[str]:
    """Fail closed on unmodeled in-combat survival changes and combatant creation."""
    text = re.sub(r"\s+", " ", str(actions or "")).strip()
    issues: list[str] = []
    source_reductions = len(_HP_MAX_REDUCTION.findall(text))
    modeled = _modeled_max_hp_riders(runtime_attacks)
    if source_reductions > len(modeled):
        issues.append("unsupported-survival-rider:hit-point-maximum-reduction")
    typed_source = [damage_type.lower() for damage_type in _TYPED_HP_MAX_REDUCTION.findall(text)]
    typed_runtime = [
        attack.max_hp_reduction.damage_type.value
        for attack in modeled
        if attack.max_hp_reduction is not None and attack.max_hp_reduction.damage_type is not None
    ]
    if any(typed_source.count(damage_type) > typed_runtime.count(damage_type) for damage_type in set(typed_source)):
        issues.append("survival-rider-damage-type-mismatch")
    if _COMBATANT_CREATION.search(text):
        issues.append("unsupported-combatant-creation-action")
    return issues
