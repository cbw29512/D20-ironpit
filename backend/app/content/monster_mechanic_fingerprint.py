from __future__ import annotations

import re
from collections.abc import Mapping

from app.content.monster_combat_scope import (
    base_feature_name,
    combat_math_relevant,
    feature_blocks,
    strip_post_combat_outcomes,
)
from app.content.monster_trait_source_audit import parse_trait_names

_TEXT_FIELDS = ("traits", "actions", "bonusActions", "reactions", "legendaryActions")
_SECTION_LABELS = {
    "traits": "trait",
    "actions": "action",
    "bonusActions": "bonus-action",
    "reactions": "reaction",
    "legendaryActions": "legendary-action",
}
_CONDITIONS = (
    "blinded", "charmed", "deafened", "frightened", "grappled", "incapacitated",
    "invisible", "paralyzed", "petrified", "poisoned", "prone", "restrained",
    "stunned", "unconscious",
)
_DAMAGE_TYPES = (
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
)
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("attack-roll", re.compile(r"\b(?:melee|ranged|melee or ranged)\s+(?:spell\s+)?attack roll\b", re.I)),
    ("multiattack", re.compile(r"\bmultiattack\b", re.I)),
    ("saving-throw", re.compile(r"\bsaving throw\b|\bDC\s*\d+\s+(?:STR|DEX|CON|INT|WIS|CHA)\b", re.I)),
    ("advantage", re.compile(r"\badvantage\b", re.I)),
    ("disadvantage", re.compile(r"\bdisadvantage\b", re.I)),
    ("injured-target-advantage", re.compile(r"\badvantage\b[^.]{0,120}\b(?:doesn['’]t have all|has less than (?:its|the) maximum|missing)\b[^.]{0,80}\bhit points?\b", re.I)),
    ("flat-modifier", re.compile(r"\bbonus to\b|\bpenalty to\b|\bAC increases?\b|\bAC decreases?\b", re.I)),
    ("bonus-die", re.compile(r"\badd(?:s)?\s+\d*d\d+\b|\bsubtract(?:s)?\s+\d*d\d+\b", re.I)),
    ("ability-score-change", re.compile(r"\b(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+score\s+(?:decreases?|increases?|is reduced|is increased)\b", re.I)),
    ("ability-score-zero-death", re.compile(r"\bdies?\b[^.]{0,100}\b(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\b[^.]{0,80}\b0\b", re.I)),
    ("attachment-state", re.compile(r"\battaches?\s+to\b|\bwhile attached\b|\bdetach(?:es|ed|ing)?\b", re.I)),
    ("temporary-hp", re.compile(r"\btemporary hit points?\b", re.I)),
    ("healing", re.compile(r"\bregains?\s+\d+|\bregains? hit points?\b|\bheals?\b", re.I)),
    ("max-hp-change", re.compile(r"\bhit point maximum\b", re.I)),
    ("regeneration", re.compile(r"\bregeneration\b|\bregains?\s+\d+\s+hit points?\s+at the start\b", re.I)),
    ("recharge", re.compile(r"\brecharge\s+\d", re.I)),
    ("limited-use", re.compile(r"\b\d+\s*/\s*(?:day|rest)\b|\bonce per (?:day|rest)\b", re.I)),
    ("reaction", re.compile(r"\breaction\b", re.I)),
    ("bonus-action", re.compile(r"\bbonus action\b", re.I)),
    ("aura", re.compile(r"\baura\b|\bwithin\s+\d+\s+feet\b", re.I)),
    ("start-turn", re.compile(r"\bstart of (?:its|the|each|a creature'?s|target'?s) turn\b", re.I)),
    ("end-turn", re.compile(r"\bend of (?:its|the|each|a creature'?s|target'?s) turn\b", re.I)),
    ("repeat-save", re.compile(r"\brepeat(?:s)? the saving throw\b|\brepeats? the save\b", re.I)),
    ("concentration", re.compile(r"\bconcentration\b", re.I)),
    ("zero-hp-effect", re.compile(r"\b0 hit points\b|\breduced to 0\b|\bdrops? to 0\b", re.I)),
    ("death-trigger", re.compile(r"\bwhen (?:it|the creature) dies\b|\bupon death\b", re.I)),
    ("spellcasting", re.compile(r"\bspellcasting\b|\bspell attack\b|\bspell save DC\b", re.I)),
    ("summoning", re.compile(r"\bsummons?\b|\bcreates?\b[^.]{0,80}\b(?:creature|monster|specter|zombie|skeleton)\b", re.I)),
    ("transformation", re.compile(r"\bshapechanger\b|\bshapechange\b|\btransforms?\b|\bchanges? form\b", re.I)),
    ("legendary", re.compile(r"\blegendary action\b|\blegendary resistance\b", re.I)),
)
_COMPLEXITY_WEIGHTS = {
    "attack-roll": 1, "multiattack": 1, "saving-throw": 2, "advantage": 1,
    "disadvantage": 1, "injured-target-advantage": 1, "flat-modifier": 2,
    "bonus-die": 2, "ability-score-change": 4, "ability-score-zero-death": 3,
    "attachment-state": 6, "temporary-hp": 2, "healing": 2, "max-hp-change": 3,
    "regeneration": 3, "recharge": 2, "limited-use": 2, "reaction": 2,
    "bonus-action": 1, "aura": 3, "start-turn": 2, "end-turn": 2,
    "repeat-save": 3, "concentration": 3, "zero-hp-effect": 3,
    "death-trigger": 3, "spellcasting": 4, "summoning": 7, "transformation": 7,
    "legendary": 6, "damage": 1, "resistance": 1, "vulnerability": 1,
    "immunity": 1, "source-parse-error": 10,
}


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
    if re.search(r"\bdamage resistance\b|\bresistant to\b", raw, re.I): mechanics.add("resistance")
    if re.search(r"\bdamage vulnerabilit|\bvulnerable to\b", raw, re.I): mechanics.add("vulnerability")
    if re.search(r"\bdamage immunit|\bimmune to\b", raw, re.I): mechanics.add("immunity")
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
    if re.search(r"\bdamage resistance\b|\bresistant to\b", raw, re.I): mechanics.add("resistance")
    if re.search(r"\bdamage vulnerabilit|\bvulnerable to\b", raw, re.I): mechanics.add("vulnerability")
    if re.search(r"\bdamage immunit|\bimmune to\b", raw, re.I): mechanics.add("immunity")
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
        total += 1 if mechanic.startswith("damage:") or mechanic.startswith("condition:") else _COMPLEXITY_WEIGHTS.get(mechanic, 2)
    return total


def mechanic_fingerprint(row: Mapping[str, object]) -> str:
    mechanics = normalized_monster_mechanics(row)
    return "+".join(mechanics) if mechanics else "combat-math-none"
