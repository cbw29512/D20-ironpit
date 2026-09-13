from __future__ import annotations

from functools import lru_cache
import logging
import re

from app.domain.actions import ConditionName
from app.domain.combatants import DamageType

logger = logging.getLogger(__name__)
_DAMAGE_TYPES = {item.value for item in DamageType}
_CONDITIONS = {
    "blinded", "charmed", "deafened", "exhaustion", "frightened", "grappled",
    "incapacitated", "invisible", "paralyzed", "petrified", "poisoned", "prone",
    "restrained", "stunned", "unconscious",
}
_LABELS = (
    "Skills", "Vulnerabilities", "Resistances", "Immunities", "Gear", "Senses",
    "Languages", "CR", "Traits", "Actions", "Bonus Actions", "Reactions", "Legendary Actions",
)
_LABEL_PATTERN = "|".join(re.escape(label) for label in sorted(_LABELS, key=len, reverse=True))


def _section(raw_text: str, label: str) -> str:
    match = re.search(
        rf"\b{re.escape(label)}\s+(.+?)(?=\s+(?:{_LABEL_PATTERN})\b|$)",
        raw_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def _tokens(value: str) -> list[str]:
    if not value:
        return []
    return [
        re.sub(r"^and\s+", "", token.strip().lower())
        for token in re.split(r"[,;]", value)
        if token.strip()
    ]


def _damage_types(value: str, label: str) -> set[str]:
    result: set[str] = set()
    for token in _tokens(value):
        if token not in _DAMAGE_TYPES:
            raise ValueError(f"Unsupported SRD {label} defense clause: {token!r}")
        result.add(token)
    return result


@lru_cache(maxsize=512)
def _parse_defense_text(raw_text: str) -> tuple[frozenset[str], frozenset[str], frozenset[str], frozenset[str]]:
    try:
        vulnerabilities = _damage_types(_section(raw_text, "Vulnerabilities"), "vulnerability")
        resistances = _damage_types(_section(raw_text, "Resistances"), "resistance")
        damage_immunities: set[str] = set()
        condition_immunities: set[str] = set()
        for token in _tokens(_section(raw_text, "Immunities")):
            if token in _DAMAGE_TYPES:
                damage_immunities.add(token)
            elif token in _CONDITIONS:
                condition_immunities.add(token)
            else:
                raise ValueError(f"Unsupported SRD immunity clause: {token!r}")
        return tuple(map(frozenset, (vulnerabilities, resistances, damage_immunities, condition_immunities)))
    except Exception:
        logger.exception("Failed to parse SRD defense profile.")
        raise


def parse_defense_profile(row: dict[str, object]) -> dict[str, set[str]]:
    """Parse exact combat defenses from a 2024 SRD monster stat block; reject lossy clauses."""
    try:
        values = _parse_defense_text(str(row.get("rawText", "")))
        keys = ("damage_vulnerabilities", "damage_resistances", "damage_immunities", "condition_immunities")
        return {key: set(value) for key, value in zip(keys, values, strict=True)}
    except Exception:
        logger.exception("Failed to resolve cached SRD defense profile.")
        raise


def defense_issues(template, row: dict[str, object]) -> list[str]:
    expected = parse_defense_profile(row)
    actual = {
        "damage_vulnerabilities": {str(item) for item in template.damage_vulnerabilities},
        "damage_resistances": {str(item) for item in template.damage_resistances},
        "damage_immunities": {str(item) for item in template.damage_immunities},
        "condition_immunities": {str(item) for item in template.condition_immunities},
    }
    return [f"{name.replace('_', '-')}-mismatch" for name in expected if actual[name] != expected[name]]
