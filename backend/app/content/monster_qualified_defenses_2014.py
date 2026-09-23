from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.damage_defenses import QualifiedDamageDefense
from app.domain.weapons import DamageType

logger = logging.getLogger(__name__)
_NONMAGICAL_ATTACK = re.compile(
    r"^(?P<types>.+?) from nonmagical attacks(?: that aren't (?P<material>[a-z]+))?$",
    re.IGNORECASE,
)
_DAMAGE_TYPES = {item.value: item for item in DamageType}


def _parse_damage_types(value: str) -> list[DamageType]:
    try:
        normalized = re.sub(r",\s*and\s+", ",", value.strip().lower())
        normalized = re.sub(r"\s+and\s+", ",", normalized)
        names = [item.strip() for item in normalized.split(",") if item.strip()]
        if not names or any(name not in _DAMAGE_TYPES for name in names):
            raise ValueError(f"Unsupported qualified defense damage types: {value!r}")
        return [_DAMAGE_TYPES[name] for name in names]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to parse qualified defense damage types %r.", value)
        raise RuntimeError("Qualified defense damage types could not be parsed.") from exc


def parse_qualified_defense_2014(clause: str) -> QualifiedDamageDefense | None:
    """Translate supported SRD 5.1 source clauses into one universal defense rule."""
    try:
        normalized = clause.strip().lower().replace("’", "'")
        match = _NONMAGICAL_ATTACK.fullmatch(normalized)
        if match is None:
            return None
        material = match.group("material")
        return QualifiedDamageDefense(
            kind="resistance",
            damage_types=_parse_damage_types(match.group("types")),
            attack_only=True,
            magical=False,
            bypass_materials=[material] if material else [],
            source_name="Damage Resistances",
            source_text=clause,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to parse 2014 qualified defense clause %r.", clause)
        raise RuntimeError("2014 qualified defense clause could not be parsed.") from exc


def qualified_damage_defenses_2014(monster: SourceMonster2014) -> list[QualifiedDamageDefense]:
    """Return every supported qualified defense declared by a 2014 monster."""
    try:
        return [
            parsed
            for clause in monster.unsupported_defense_text
            if (parsed := parse_qualified_defense_2014(clause)) is not None
        ]
    except Exception as exc:
        logger.exception("Failed to bind qualified defenses for %s.", monster.name)
        raise RuntimeError("2014 qualified defenses could not be bound.") from exc


def unsupported_defense_clauses_2014(monster: SourceMonster2014) -> tuple[str, ...]:
    """Keep unrecognized defense clauses fail-closed."""
    try:
        return tuple(
            clause
            for clause in monster.unsupported_defense_text
            if parse_qualified_defense_2014(clause) is None
        )
    except Exception as exc:
        logger.exception("Failed to classify defense clauses for %s.", monster.name)
        raise RuntimeError("2014 defense clauses could not be classified.") from exc
