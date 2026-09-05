from __future__ import annotations

import logging
import re

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_TARGET_MISSING_HP = "target_missing_hit_points"
_ATTACKER_BLOODIED = "attacker_bloodied"
_MAGICAL_EFFECT = "magical_effect"
_MISSING_HP_ADVANTAGE = re.compile(
    r"\bAdvantage\b[^.]{0,240}\bdoesn[’']t have all (?:its|their) Hit Points\b",
    re.IGNORECASE,
)
_BLOODIED_FRENZY = re.compile(
    r"\bBloodied Frenzy\b[^.]*\.\s*While Bloodied,[^.]{0,240}\bAdvantage on attack rolls and saving throws\b",
    re.IGNORECASE,
)
_MAGIC_RESISTANCE = re.compile(
    r"\bMagic Resistance\b[^.]*\.\s*[^.]{0,240}\bAdvantage on saving throws against spells and other magical effects\b",
    re.IGNORECASE,
)


def _source_text(row: dict[str, object]) -> str:
    return "\n".join((str(row.get("traits", "")), str(row.get("actions", ""))))


def source_advantage_triggers(row: dict[str, object]) -> tuple[list[str], list[str]]:
    """Compile source-owned Advantage conditions into shared runtime trigger ids."""
    source = _source_text(row)
    attack: list[str] = []
    saves: list[str] = []
    if _MISSING_HP_ADVANTAGE.search(source):
        attack.append(_TARGET_MISSING_HP)
    if _BLOODIED_FRENZY.search(source):
        attack.append(_ATTACKER_BLOODIED)
        saves.append(_ATTACKER_BLOODIED)
    if _MAGIC_RESISTANCE.search(source):
        saves.append(_MAGICAL_EFFECT)
    return attack, saves


def _trigger_issues(kind: str, expected: list[str], runtime: list[str]) -> list[str]:
    expected_set = set(expected); runtime_set = set(runtime)
    issues = [
        f"{kind}-advantage-runtime-missing:{trigger.replace('_', '-')}"
        for trigger in sorted(expected_set - runtime_set)
    ]
    issues.extend(
        f"{kind}-advantage-source-missing:{trigger.replace('_', '-')}"
        for trigger in sorted(runtime_set - expected_set)
    )
    return issues


def attack_advantage_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Fail closed when SRD and runtime disagree on certified roll-Advantage triggers."""
    try:
        expected_attack, expected_save = source_advantage_triggers(row)
        issues = _trigger_issues("attack", expected_attack, template.attack_roll_advantage_triggers)
        issues.extend(_trigger_issues("save", expected_save, template.saving_throw_advantage_triggers))
        return issues
    except Exception:
        logger.exception("Attack Advantage source audit failed for %s.", template.id)
        raise
