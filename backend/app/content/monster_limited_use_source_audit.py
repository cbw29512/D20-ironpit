from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.content.monster_combat_scope import base_feature_name, combat_math_relevant, feature_blocks
from app.content.monster_limited_use_source import limited_use_spec, parse_limited_use_names
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def _resource_matches(template: CombatantTemplate, resource_id: str | None, resource_cost: int | None, fingerprint: str) -> bool:
    if not resource_id or resource_cost != 1:
        return False
    spec = limited_use_spec(fingerprint)
    resource = next((item for item in template.resources if item.id == resource_id), None)
    if resource is None or resource.max_uses != spec.max_uses:
        return False
    if spec.recharge_minimum is None:
        return resource.recharge is None
    return (
        resource.recharge is not None
        and resource.recharge.minimum == spec.recharge_minimum
        and resource.recharge.maximum == spec.recharge_maximum
        and resource.recharge.die_size == 6
    )


def _save_supported(template: CombatantTemplate, fingerprint: str) -> bool:
    spec = limited_use_spec(fingerprint)
    if spec.section not in {"actions", "bonusActions"}:
        return False
    action = next(
        (item for item in template.saving_throw_actions if base_feature_name(item.name) == spec.base_name),
        None,
    )
    if action is None:
        return False
    if spec.section == "bonusActions" and action.action_cost != "bonus_action":
        return False
    if spec.section == "actions" and action.action_cost != "action":
        return False
    return _resource_matches(template, action.resource_id, action.resource_cost, fingerprint)


def _attack_supported(template: CombatantTemplate, fingerprint: str) -> bool:
    spec = limited_use_spec(fingerprint)
    if spec.section != "actions":
        return False
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    matching = [item for item in attacks if base_feature_name(item.weapon.name) == spec.base_name]
    return bool(matching) and all(
        _resource_matches(template, item.resource_id, item.resource_cost, fingerprint) for item in matching
    )


def limited_use_source_relevant(row: dict[str, object], fingerprint: str) -> bool:
    spec = limited_use_spec(fingerprint)
    source = row.get(spec.section, "")
    headings = parse_trait_names(source, preserve_annotations=True)
    blocks = feature_blocks(source, headings)
    return combat_math_relevant(blocks[spec.heading])


def limited_use_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Certify generic finite-use resources; ignore limited movement/sensory/presentation features."""
    expected = parse_limited_use_names(row)
    issues: list[str] = []
    if template.source_limited_use_names != expected:
        issues.append("source-limited-use-fingerprint-mismatch")
    for name in expected:
        if _save_supported(template, name) or _attack_supported(template, name):
            continue
        if not limited_use_source_relevant(row, name):
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        issues.append(f"uncertified-limited-use:{slug}")
    return issues


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
