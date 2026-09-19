from __future__ import annotations

import hashlib
import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_FIELDS = ("traits", "actions", "bonusActions", "reactions")
_CASTING = re.compile(r"\bSpellcasting\b|\bcast(?:s|ing)?\b", re.IGNORECASE)
_SPELL_GROUP = re.compile(
    r"\b(At Will|\d+/Day(?: Each)?):\s*(.*?)(?=\s+(?:At Will|\d+/Day(?: Each)?):|$)",
    re.IGNORECASE,
)
# Explicitly certified as irrelevant to the standard flat/open Iron Pit outcome.
# These spells are never selected as combat actions; unknown additions fail closed.
_ARENA_NEUTRAL_SPELLS = frozenset({
    "Animal Messenger", "Clairvoyance", "Detect Evil and Good", "Detect Magic",
    "Druidcraft", "Speak with Animals",
})
# Printed spells whose full battlefield semantics are intentionally replaced by a simpler
# real D&D damaging spell at roughly the same spell level for the Iron Pit arena.
# The replacement is content policy, not a combat-engine special case.
_ARENA_SPELL_SUBSTITUTIONS: dict[str, tuple[str, int]] = {
    "Entangle": ("guiding-bolt", 1),
    "Moonbeam": ("inflict-wounds", 2),
    "Thunderwave": ("guiding-bolt", 1),
}
# Printed spells whose relevant arena behavior is directly represented by an existing
# generic spell action.
_ARENA_MODELED_SPELLS: dict[str, tuple[str, int]] = {
    "Long-strider": ("longstrider", 1),
}


def _normalized(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def spellcasting_source_text(row: dict[str, object]) -> str:
    """Retain complete source sections that contain casting rules, not guessed spell metadata."""
    chunks: list[str] = []
    for field in _FIELDS:
        text = _normalized(row.get(field, ""))
        if text and _CASTING.search(text):
            chunks.append(f"{field}={text}")
    return "\n".join(chunks)


def spellcasting_fingerprint(row: dict[str, object]) -> str | None:
    text = spellcasting_source_text(row)
    return hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None


def _trim_neighbor_heading(spell: str, current_name: str) -> str:
    """Remove a page-neighbor monster heading appended to the final spell token."""
    for monster_name in sorted(
        (str(item["name"]) for item in load_monster_rows() if str(item["name"]) != current_name),
        key=len,
        reverse=True,
    ):
        suffix = f" {monster_name}"
        if spell.endswith(suffix):
            return spell[:-len(suffix)].rstrip()
    return spell


def _spell_groups(row: dict[str, object]) -> list[tuple[str, list[str]]]:
    text = spellcasting_source_text(row)
    current_name = str(row.get("name", ""))
    return [
        (
            label,
            [
                _trim_neighbor_heading(spell.strip(), current_name)
                for spell in group.split(",")
                if spell.strip()
            ],
        )
        for label, group in _SPELL_GROUP.findall(text)
    ]


def _printed_spell_names(row: dict[str, object]) -> set[str]:
    return {spell for _, spells in _spell_groups(row) for spell in spells}


def _handled_spell_names() -> set[str]:
    return set(_ARENA_NEUTRAL_SPELLS) | set(_ARENA_SPELL_SUBSTITUTIONS) | set(_ARENA_MODELED_SPELLS)


def arena_neutral_spellcasting(row: dict[str, object]) -> bool:
    """Compatibility name: true when every printed spell has an explicit Iron Pit arena policy."""
    spells = _printed_spell_names(row)
    return bool(spells) and spells <= _handled_spell_names()


def _expected_runtime_spell_ids(row: dict[str, object]) -> set[str]:
    ids = {
        runtime_id
        for spell in _printed_spell_names(row)
        for runtime_id, _ in [
            _ARENA_SPELL_SUBSTITUTIONS.get(spell)
            or _ARENA_MODELED_SPELLS.get(spell)
            or (None, 0)
        ]
        if runtime_id is not None
    }
    return ids


def _uses_from_label(label: str) -> int | None:
    if label.casefold() == "at will":
        return None
    match = re.match(r"(\d+)/Day", label, re.IGNORECASE)
    if match is None:
        raise ValueError(f"Unsupported monster spell-use label: {label!r}")
    return int(match.group(1))


def _expected_slot_uses(row: dict[str, object]) -> dict[int, int]:
    totals: dict[int, int] = {}
    for label, spells in _spell_groups(row):
        uses = _uses_from_label(label)
        for spell in spells:
            if spell in _ARENA_NEUTRAL_SPELLS:
                continue
            binding = _ARENA_SPELL_SUBSTITUTIONS.get(spell) or _ARENA_MODELED_SPELLS.get(spell)
            if binding is None or uses is None:
                continue
            _, level = binding
            totals[level] = totals.get(level, 0) + uses
    return totals


def _runtime_spell_ids(template: CombatantTemplate) -> set[str]:
    return {
        *(action.id for action in template.spell_save_actions),
        *(action.id for action in template.spell_attack_actions),
        *(action.id for action in template.defensive_spell_actions),
    }


def _runtime_slot_uses(template: CombatantTemplate) -> dict[int, int]:
    uses: dict[int, int] = {}
    for resource in template.resources:
        match = re.fullmatch(r"spell-slot-(\d+)", resource.id)
        if match:
            uses[int(match.group(1))] = resource.max_uses
    return uses


def spellcasting_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Fail closed unless every printed spell is neutral, modeled, or explicitly substituted."""
    expected = spellcasting_fingerprint(row)
    issues: list[str] = []
    if template.source_spellcasting_fingerprint != expected:
        issues.append("source-spellcasting-fingerprint-mismatch")
    if expected is None:
        return issues
    if not arena_neutral_spellcasting(row):
        issues.extend(("uncertified-monster-spellcasting", "spell-concentration-source-not-vendored"))
        return issues
    if _runtime_spell_ids(template) != _expected_runtime_spell_ids(row):
        issues.append("monster-spell-package-mismatch")
    if _runtime_slot_uses(template) != _expected_slot_uses(row):
        issues.append("monster-spell-resource-mismatch")
    return issues


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_spellcasting_fingerprint(name: str) -> str | None:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return spellcasting_fingerprint(row)


def complete_monster_spellcasting_fingerprints(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={"source_spellcasting_fingerprint": source_spellcasting_fingerprint(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception:
        logger.exception("Failed to derive canonical monster spellcasting fingerprints from SRD source.")
        raise
