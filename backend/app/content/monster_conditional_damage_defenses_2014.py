from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_damage_absorption import damage_absorptions_from_source
from app.domain.damage_sources import (
    ConditionalDamageDefense,
    DamageDefenseKind,
    DamageSourceQualifier,
)
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)
_CLAUSE = re.compile(
    r"^(?P<types>.+?)\s+from nonmagical attacks(?: that aren't (?P<bypass>silvered|adamantine))?$"
)
_TYPE_SPLIT = re.compile(r",|\band\b")
_BYPASS = {
    "silvered": DamageSourceQualifier.SILVERED,
    "adamantine": DamageSourceQualifier.ADAMANTINE,
}
_DAMAGE_TYPES = {item.value: item for item in DamageType}


def _normalize(text: str) -> str:
    return text.lower().replace("\u2019", "'").replace("\u2018", "'")


def _damage_types(raw_types: str) -> list[DamageType] | None:
    types: list[DamageType] = []
    for token in _TYPE_SPLIT.split(raw_types):
        name = token.strip()
        if not name:
            continue
        damage_type = _DAMAGE_TYPES.get(name)
        if damage_type is None:
            return None
        if damage_type not in types:
            types.append(damage_type)
    return types or None


def _kind_for_clause(monster: SourceMonster2014, clause: str) -> DamageDefenseKind | None:
    needle = _normalize(clause)
    in_resistance = needle in _normalize(monster.damage_resistances_text or "")
    in_immunity = needle in _normalize(monster.damage_immunities_text or "")
    if in_resistance == in_immunity:
        return None
    return DamageDefenseKind.RESISTANCE if in_resistance else DamageDefenseKind.IMMUNITY


def _parse_clause(monster: SourceMonster2014, clause: str) -> ConditionalDamageDefense | None:
    match = _CLAUSE.match(_normalize(clause.strip()))
    if match is None:
        return None
    damage_types = _damage_types(match.group("types"))
    kind = _kind_for_clause(monster, clause)
    if damage_types is None or kind is None:
        return None
    forbidden = [DamageSourceQualifier.MAGICAL]
    bypass = _BYPASS.get(match.group("bypass") or "")
    if bypass is not None:
        forbidden.append(bypass)
    slug = "-".join(item.value for item in damage_types)
    forbid_slug = "-".join(item.value for item in forbidden)
    return ConditionalDamageDefense(
        id=f"conditional-{kind.value}-{slug}-forbid-{forbid_slug}",
        kind=kind,
        damage_types=damage_types,
        required_source_qualifiers=[DamageSourceQualifier.ATTACK],
        forbidden_source_qualifiers=forbidden,
    )


def remaining_unsupported_defense_text_2014(monster: SourceMonster2014) -> list[str]:
    """Return printed defense clauses that the shared conditional primitive cannot bind."""
    try:
        return [clause for clause in monster.unsupported_defense_text if _parse_clause(monster, clause) is None]
    except Exception:
        logger.exception("Failed to classify remaining 2014 defense text for %s.", monster.name)
        raise


def conditional_damage_defenses_2014(monster: SourceMonster2014) -> list[ConditionalDamageDefense]:
    """Bind printed nonmagical/silvered/adamantine BPS defenses to the shared primitive."""
    try:
        defenses: list[ConditionalDamageDefense] = []
        for clause in monster.unsupported_defense_text:
            parsed = _parse_clause(monster, clause)
            if parsed is not None:
                defenses.append(parsed)
        return defenses
    except Exception:
        logger.exception("Failed to bind 2014 conditional damage defenses for %s.", monster.name)
        raise


def template_defense_fields_2014(monster: SourceMonster2014) -> dict[str, object]:
    """Typed plus conditional defenses compiled from pinned 2014 source text."""
    try:
        return {
            "damage_resistances": [item.lower() for item in monster.damage_resistances],
            "damage_vulnerabilities": [item.lower() for item in monster.damage_vulnerabilities],
            "damage_immunities": [item.lower() for item in monster.damage_immunities],
            "damage_absorptions": damage_absorptions_from_source(
                monster.source_traits, {item.lower() for item in monster.damage_immunities},
            ),
            "condition_immunities": [item.lower() for item in monster.condition_immunities],
            "conditional_damage_defenses": conditional_damage_defenses_2014(monster),
        }
    except Exception:
        logger.exception("Failed to compile 2014 defense fields for %s.", monster.name)
        raise
