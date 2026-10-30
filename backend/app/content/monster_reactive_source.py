from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.behavior_rules import BloodiedBerserkRule
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_REACTIVE = re.compile(
    r"Reactive\.\s+The [^.]+ can take one Reaction on every turn of combat\.",
    re.IGNORECASE,
)
_BERSERK = re.compile(
    r"(?P<name>Berserk)\.\s+Whenever the [^.]+ starts its turn (?:while )?Bloodied, roll 1d(?P<die>\d+)\.\s+"
    r"On a (?P<trigger>\d+), the [^.]+ goes berserk\.\s+On each of its turns while berserk, "
    r"the [^.]+ attacks the nearest creature it can see\..*?"
    r"Once the [^.]+ goes berserk, it remains (?:berserk|so) until it is destroyed or it is no longer Bloodied\.",
    re.IGNORECASE,
)


def source_bloodied_berserk_rule(source_traits: object) -> BloodiedBerserkRule | None:
    try:
        match = _BERSERK.search(str(source_traits or ""))
        if match is None:
            return None
        return BloodiedBerserkRule(
            id="berserk",
            name=match.group("name"),
            die_size=int(match.group("die")),
            trigger_minimum=int(match.group("trigger")),
        )
    except (TypeError, ValueError):
        logger.exception("Invalid Bloodied Berserk source trait.")
        raise
    except Exception as exc:
        logger.exception("Failed to parse Bloodied Berserk source trait.")
        raise RuntimeError("Bloodied Berserk source could not be parsed.") from exc


def source_reaction_refresh_each_turn(source_traits: object) -> bool:
    try:
        text = str(source_traits or "")
        return _REACTIVE.search(text) is not None
    except Exception as exc:
        logger.exception("Failed to parse per-turn Reaction refresh source.")
        raise RuntimeError("Per-turn Reaction refresh source could not be parsed.") from exc


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    try:
        return {str(row["name"]): row for row in load_monster_rows()}
    except Exception:
        logger.exception("Failed to index monster rows for per-turn Reaction refresh.")
        raise


def complete_monster_reaction_refresh(
    templates: list[CombatantTemplate],
) -> list[CombatantTemplate]:
    try:
        rows = _rows_by_name()
        completed: list[CombatantTemplate] = []
        for template in templates:
            if template.kind != "monster":
                completed.append(template)
                continue
            row = rows.get(template.name)
            if row is None:
                raise ValueError(f"No SRD source row for monster {template.name!r}.")
            completed.append(template.model_copy(update={
                "reaction_refresh_each_turn": source_reaction_refresh_each_turn(row.get("traits", "")),
                "bloodied_berserk_rule": source_bloodied_berserk_rule(row.get("traits", "")),
            }))
        return completed
    except Exception as exc:
        logger.exception("Failed to complete per-turn Reaction refresh profiles.")
        raise RuntimeError("Per-turn Reaction refresh completion failed.") from exc


def reactive_trait_issues(
    template: CombatantTemplate,
    row: dict[str, object],
) -> tuple[list[str], set[str]]:
    try:
        source = row.get("traits", "")
        expected_reactive = source_reaction_refresh_each_turn(source)
        expected_berserk = source_bloodied_berserk_rule(source)
        issues: list[str] = []
        certified: set[str] = set()
        if template.reaction_refresh_each_turn != expected_reactive:
            issues.append("reactive-source-data-mismatch")
        elif expected_reactive:
            certified.add("Reactive")
        if template.bloodied_berserk_rule != expected_berserk:
            issues.append("bloodied-berserk-source-data-mismatch")
        elif expected_berserk is not None:
            certified.add(expected_berserk.name)
        return issues, certified
    except Exception as exc:
        logger.exception("Failed reactive behavior trait audit for %s.", template.id)
        raise RuntimeError("Reactive behavior trait audit failed.") from exc
