from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Iterable

from app.content.monster_simple_save_control_parser import strip_simple_save_control_actions
from app.content.monster_simple_save_parser import strip_simple_save_actions
from app.content.monster_source_classifier import _ALLOWED_TRAITS
from app.content.monster_trait_source_audit import parse_trait_names

_CONTROL = re.compile(
    r"\b(blinded|charmed|deafened|frightened|grappled|incapacitated|paralyzed|petrified|"
    r"poisoned|prone|restrained|stunned|unconscious|push(?:es|ed)?|pull(?:s|ed)?|swallow(?:s|ed)?)\b",
    re.I,
)
_COMPLEX_PATTERNS: dict[str, re.Pattern[str]] = {
    "save-branch": re.compile(r"(?:\bSaving Throw\b|\bFailure:|\bSuccess:)", re.I),
    "temporary-hp": re.compile(r"\bTemporary Hit Points?\b", re.I),
    "healing-or-regain": re.compile(r"\bregains?\s+\d+\b", re.I),
    "teleport": re.compile(r"\bteleport\b", re.I),
    "concentration": re.compile(r"\bConcentration\b", re.I),
}


def _ordered_incidence(values: dict[str, list[str]]) -> dict[str, list[str]]:
    return {
        key: sorted(names)
        for key, names in sorted(values.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def unsupported_trait_incidence(
    rows_by_name: dict[str, dict[str, object]], names: Iterable[str]
) -> dict[str, list[str]]:
    found: dict[str, list[str]] = defaultdict(list)
    for name in names:
        try:
            traits = parse_trait_names(rows_by_name[name].get("traits", ""))
        except ValueError:
            continue
        for trait in sorted(set(traits) - _ALLOWED_TRAITS):
            found[trait].append(name)
    return _ordered_incidence(found)


def control_effect_incidence(
    rows_by_name: dict[str, dict[str, object]], names: Iterable[str]
) -> dict[str, list[str]]:
    found: dict[str, list[str]] = defaultdict(list)
    for name in names:
        actions = str(rows_by_name[name].get("actions", ""))
        effects = set()
        for match in _CONTROL.finditer(actions):
            effect = match.group(1).lower()
            if effect.startswith("push"):
                effect = "forced-push"
            elif effect.startswith("pull"):
                effect = "forced-pull"
            elif effect.startswith("swallow"):
                effect = "swallow"
            effects.add(effect)
        for effect in sorted(effects):
            found[effect].append(name)
    return _ordered_incidence(found)


def complex_action_incidence(
    rows_by_name: dict[str, dict[str, object]], names: Iterable[str]
) -> dict[str, list[str]]:
    found: dict[str, list[str]] = defaultdict(list)
    for name in names:
        actions = str(rows_by_name[name].get("actions", ""))
        residual = strip_simple_save_control_actions(strip_simple_save_actions(actions))
        for kind, pattern in _COMPLEX_PATTERNS.items():
            if pattern.search(residual):
                found[kind].append(name)
    return _ordered_incidence(found)
