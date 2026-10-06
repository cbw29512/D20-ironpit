from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_FIELDS = ("traits", "actions", "bonusActions", "reactions")
_CONNECTORS = frozenset({"a", "an", "and", "of", "or", "the", "to"})
_MARKER = re.compile(r"\((?:[^)]*(?:Recharge\s+\d(?:\s*[-–]\s*\d)?|\d+\s*/\s*Day)[^)]*)\)", re.I)


def _is_heading(value: str) -> bool:
    base = re.sub(r"\s*\([^)]*\)$", "", value).strip()
    words = base.split()
    if not words or len(value) > 100:
        return False
    return all(
        word.lower() in _CONNECTORS or re.fullmatch(r"[A-Z][A-Za-z’'\-]*", word)
        for word in words
    )


def _limited_headings(source: object) -> list[str]:
    text = re.sub(r"\s+", " ", str(source or "")).strip()
    if not text:
        return []
    names: list[str] = []
    for sentence in re.split(r"(?<=\.)\s+", text):
        candidate = sentence[:-1].strip() if sentence.endswith(".") else ""
        if candidate and _MARKER.search(candidate):
            if not _is_heading(candidate):
                raise ValueError(f"Limited-use marker is not on a parseable heading: {candidate!r}")
            names.append(candidate)
    if _MARKER.search(text) and not names:
        raise ValueError(f"SRD limited-use heading could not be parsed from: {text!r}")
    return names


def parse_limited_use_names(row: dict[str, object]) -> list[str]:
    names: list[str] = []
    for field in _FIELDS:
        names.extend(f"{field}:{name}" for name in _limited_headings(row.get(field, "")))
    return names


def _recharge_binding_matches(template: CombatantTemplate, source_name: str) -> bool:
    marker = re.search(r"\(Recharge\s+(\d)(?:\s*[-–]\s*(\d))?\)", source_name, re.I)
    if marker is None:
        return False
    action_name = re.sub(r"\s*\([^)]*\)$", "", source_name.split(":", 1)[-1]).strip()
    actions = [
        action for action in template.saving_throw_actions
        if action.name.casefold() == action_name.casefold()
    ]
    if len(actions) != 1 or actions[0].resource_id is None or actions[0].resource_cost != 1:
        return False
    resource_id = actions[0].resource_id
    resources = [
        resource for resource in template.resources
        if resource.id == resource_id and resource.max_uses == 1
    ]
    rules = [
        rule for rule in template.recharge_rules
        if rule.resource_id == resource_id
        and rule.minimum_roll == int(marker.group(1))
        and rule.die_size == 6
    ]
    return len(resources) == 1 and len(rules) == 1


def _per_day_stack_binding_matches(template: CombatantTemplate, source_name: str) -> bool:
    try:
        marker = re.search(r"\((\d+)\s*/\s*Day\)", source_name, re.I)
        if marker is None or not source_name.startswith("traits:"):
            return False
        use_cap = int(marker.group(1))
        trait_name = re.sub(
            r"\s*\([^)]*\)$", "", source_name.split(":", 1)[-1]
        ).strip()
        matches = [
            rule
            for rule in template.triggered_extra_attack_stacks
            if rule.source_name.casefold() == trait_name.casefold()
            and rule.max_uses == use_cap
        ]
        return len(matches) == 1
    except Exception:
        logger.exception(
            "Failed to certify per-day triggered stack binding for %s.",
            template.name,
        )
        raise


def _legendary_resistance_binding_matches(template: CombatantTemplate, source_name: str) -> bool:
    from app.content.monster_legendary_resistance_2014 import RESOURCE_ID, is_legendary_resistance_trait
    heading = source_name.split(":", 1)[-1].strip()
    if not is_legendary_resistance_trait(heading):
        return False
    resources = [item for item in template.resources if item.id == RESOURCE_ID]
    overrides = [item for item in template.save_success_overrides if item.source_id == RESOURCE_ID]
    return len(resources) == 1 and len(overrides) == 1


def limited_use_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Certify source limited-use markers only when a matching generic resource is bound."""
    try:
        expected = parse_limited_use_names(row)
        issues: list[str] = []
        if template.source_limited_use_names != expected:
            issues.append("source-limited-use-fingerprint-mismatch")
        for name in expected:
            if _recharge_binding_matches(template, name):
                continue
            if _per_day_stack_binding_matches(template, name):
                continue
            if _legendary_resistance_binding_matches(template, name):
                continue
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            issues.append(f"uncertified-limited-use:{slug}")
        return issues
    except Exception:
        logger.exception("Failed limited-use source audit for %s.", template.name)
        raise


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_limited_use_names(name: str) -> list[str]:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return parse_limited_use_names(row)


def complete_monster_limited_use_fingerprints(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={"source_limited_use_names": source_limited_use_names(template.name)})
            if template.kind == "monster" else template
            for template in templates
        ]
    except Exception:
        logger.exception("Failed to derive canonical monster limited-use fingerprints from SRD source.")
        raise
