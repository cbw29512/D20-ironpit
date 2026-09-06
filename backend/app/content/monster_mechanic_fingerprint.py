from __future__ import annotations

import re
from collections.abc import Mapping

from app.content.monster_combat_scope import (
    base_feature_name,
    combat_math_relevant,
    feature_blocks,
    strip_post_combat_outcomes,
)
from app.content.monster_mechanic_patterns import (
    COMPLEXITY_WEIGHTS as _COMPLEXITY_WEIGHTS,
    CONDITIONS as _CONDITIONS,
    DAMAGE_TYPES as _DAMAGE_TYPES,
    PATTERNS as _PATTERNS,
    SECTION_LABELS as _SECTION_LABELS,
    TEXT_FIELDS as _TEXT_FIELDS,
)
from app.content.monster_trait_source_audit import parse_trait_names


def _source_text(row: Mapping[str, object]) -> str:
    return "\n".join(strip_post_combat_outcomes(row.get(field, "")) for field in _TEXT_FIELDS)


def normalized_source_mechanics(source: object) -> tuple[str, ...]:
    """Normalize one source feature into reusable combat-math mechanics."""
    text = strip_post_combat_outcomes(source)
    mechanics = {name for name, pattern in _PATTERNS if pattern.search(text)}
    if re.search(r"\bdamage\b", text, re.I):
        mechanics.add("damage")
    for damage_type in _DAMAGE_TYPES:
        if re.search(rf"\b{damage_type}\s+damage\b", text, re.I):
            mechanics.add(f"damage:{damage_type}")
    for condition in _CONDITIONS:
        if re.search(rf"\b{condition}\b", text, re.I):
            mechanics.add(f"condition:{condition}")
    return tuple(sorted(mechanics))


def normalized_monster_mechanics(row: Mapping[str, object]) -> tuple[str, ...]:
    """Return combat-math mechanics only; pure movement and post-combat outcomes never enter the fingerprint."""
    mechanics = set(normalized_source_mechanics(_source_text(row)))
    raw = str(row.get("rawText", "") or "")
    if re.search(r"\bdamage resistance\b|\bresistant to\b", raw, re.I):
        mechanics.add("resistance")
    if re.search(r"\bdamage vulnerabilit|\bvulnerable to\b", raw, re.I):
        mechanics.add("vulnerability")
    if re.search(r"\bdamage immunit|\bimmune to\b", raw, re.I):
        mechanics.add("immunity")
    return tuple(sorted(mechanics))


def mechanic_equivalence_fingerprint(mechanics: tuple[str, ...]) -> str:
    """Collapse data parameters that should not create separate engine branches.

    Damage type and amount are data consumed by the universal typed-damage path, so
    fire/cold/etc. attacks can share one mechanic family. Conditions remain explicit
    because each condition has distinct combat-math semantics.
    """
    normalized = {
        "damage:typed" if mechanic.startswith("damage:") else mechanic
        for mechanic in mechanics
    }
    return "+".join(sorted(normalized)) if normalized else "combat-math-none"


def _statblock_defense_record(row: Mapping[str, object]) -> dict[str, object] | None:
    raw = str(row.get("rawText", "") or "")
    mechanics: set[str] = set()
    if re.search(r"\bdamage resistance\b|\bresistant to\b", raw, re.I):
        mechanics.add("resistance")
    if re.search(r"\bdamage vulnerabilit|\bvulnerable to\b", raw, re.I):
        mechanics.add("vulnerability")
    if re.search(r"\bdamage immunit|\bimmune to\b", raw, re.I):
        mechanics.add("immunity")
    if not mechanics:
        return None
    ordered = tuple(sorted(mechanics))
    return {
        "monster": str(row.get("name", "")),
        "section": "statblock",
        "source_name": "Damage Defenses",
        "normalized_name": "Damage Defenses",
        "mechanics": ordered,
        "fingerprint": "+".join(ordered),
        "equivalence_fingerprint": mechanic_equivalence_fingerprint(ordered),
        "parse_error": False,
    }


def source_ability_records(row: Mapping[str, object]) -> tuple[dict[str, object], ...]:
    """Return every combat-relevant source feature as an independently comparable record.

    Exact printed headings are preserved for logs/audits. A parser failure is emitted as
    an explicit record rather than silently dropping source material from the registry.
    """
    records: list[dict[str, object]] = []
    monster = str(row.get("name", ""))
    for field in _TEXT_FIELDS:
        source = strip_post_combat_outcomes(row.get(field, ""))
        if not source:
            continue
        try:
            headings = parse_trait_names(source, preserve_annotations=True)
            blocks = feature_blocks(source, headings)
        except ValueError:
            if combat_math_relevant(source):
                mechanics = tuple(sorted({*normalized_source_mechanics(source), "source-parse-error"}))
                records.append({
                    "monster": monster,
                    "section": _SECTION_LABELS[field],
                    "source_name": f"[Unparsed {field}]",
                    "normalized_name": f"[Unparsed {field}]",
                    "mechanics": mechanics,
                    "fingerprint": "+".join(mechanics),
                    "equivalence_fingerprint": mechanic_equivalence_fingerprint(mechanics),
                    "parse_error": True,
                })
            continue
        for heading, block in blocks.items():
            if not combat_math_relevant(block):
                continue
            mechanics = normalized_source_mechanics(block)
            records.append({
                "monster": monster,
                "section": _SECTION_LABELS[field],
                "source_name": heading,
                "normalized_name": base_feature_name(heading),
                "mechanics": mechanics,
                "fingerprint": "+".join(mechanics) if mechanics else "combat-math-none",
                "equivalence_fingerprint": mechanic_equivalence_fingerprint(mechanics),
                "parse_error": False,
            })
    defense_record = _statblock_defense_record(row)
    if defense_record is not None:
        records.append(defense_record)
    return tuple(records)


def mechanic_complexity(mechanics: tuple[str, ...]) -> int:
    total = 0
    for mechanic in mechanics:
        total += (
            1
            if mechanic.startswith("damage:") or mechanic.startswith("condition:")
            else _COMPLEXITY_WEIGHTS.get(mechanic, 2)
        )
    return total


def mechanic_fingerprint(row: Mapping[str, object]) -> str:
    mechanics = normalized_monster_mechanics(row)
    return "+".join(mechanics) if mechanics else "combat-math-none"
