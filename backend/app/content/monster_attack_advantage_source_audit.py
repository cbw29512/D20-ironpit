from __future__ import annotations

import logging
import re

from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)
_TARGET_MISSING_HP = "target_missing_hit_points"
_ATTACKER_BLOODIED = "attacker_bloodied"
_MISSING_HP_ADVANTAGE = re.compile(
    r"\bAdvantage\b[^.]{0,240}\bdoesn[’']t have all (?:its|their) Hit Points\b",
    re.IGNORECASE,
)
_BLOODIED_FRENZY = re.compile(
    r"\bBloodied Frenzy\b[^.]*\.\s*While Bloodied,[^.]{0,240}\bAdvantage on attack rolls and saving throws\b",
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
    return attack, saves


def attack_advantage_issues(template: CombatantTemplate, row: dict[str, object]) -> list[str]:
    """Fail closed when SRD and runtime disagree on certified roll-Advantage triggers."""
    try:
        expected_attack, expected_save = source_advantage_triggers(row)
        source_missing_hp = _TARGET_MISSING_HP in expected_attack
        runtime_missing_hp = _TARGET_MISSING_HP in template.attack_roll_advantage_triggers
        source_bloodied = _ATTACKER_BLOODIED in expected_attack
        runtime_bloodied_attack = _ATTACKER_BLOODIED in template.attack_roll_advantage_triggers
        runtime_bloodied_save = _ATTACKER_BLOODIED in template.saving_throw_advantage_triggers
        issues: list[str] = []
        if source_missing_hp and not runtime_missing_hp:
            issues.append("attack-advantage-runtime-missing:target-missing-hit-points")
        elif runtime_missing_hp and not source_missing_hp:
            issues.append("attack-advantage-source-missing:target-missing-hit-points")
        if source_bloodied and not runtime_bloodied_attack:
            issues.append("attack-advantage-runtime-missing:attacker-bloodied")
        elif runtime_bloodied_attack and not source_bloodied:
            issues.append("attack-advantage-source-missing:attacker-bloodied")
        if _ATTACKER_BLOODIED in expected_save and not runtime_bloodied_save:
            issues.append("save-advantage-runtime-missing:attacker-bloodied")
        elif runtime_bloodied_save and _ATTACKER_BLOODIED not in expected_save:
            issues.append("save-advantage-source-missing:attacker-bloodied")
        return issues
    except Exception:
        logger.exception("Attack Advantage source audit failed for %s.", template.id)
        raise
