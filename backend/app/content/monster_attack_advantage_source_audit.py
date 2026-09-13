from __future__ import annotations

import logging
import re

from app.domain.models import WeaponAttack

logger = logging.getLogger(__name__)
_TARGET_NOT_FULL = r"with\s+advantage\s+if\s+the\s+target\s+(?:doesn['’]t|does\s+not)\s+have\s+all\s+its\s+hit\s+points"
_SOURCE_GRAPPLE = r"with\s+advantage\s+if\s+the\s+target\s+is\s+grappled\s+by\s+the\s+[^)]+"
_BLOOD_FRENZY = r"\bblood\s+frenzy\.\s+the\s+[^.]+?has\s+advantage\s+on\s+attack\s+rolls\s+against\s+any\s+creature\s+that\s+(?:doesn['’]t|does\s+not)\s+have\s+all\s+its\s+hit\s+points"


def _source_has_header_clause(name: str, clause: str, actions: str) -> bool:
    return bool(re.search(
        rf"\b{name}\.\s+(?:melee|ranged|melee\s+or\s+ranged)\s+attack\s+roll:[^.]*?\(\s*{clause}\s*\)",
        actions,
        re.IGNORECASE,
    ))


def conditional_attack_advantage_issues(attack: WeaponAttack, actions: str, traits: str = "") -> list[str]:
    try:
        name = re.escape(attack.weapon.name)
        expected = {
            "target_not_full_hp": int(
                _source_has_header_clause(name, _TARGET_NOT_FULL, actions)
                or bool(re.search(_BLOOD_FRENZY, traits, re.IGNORECASE))
            ),
            "target_grappled_by_source": int(_source_has_header_clause(name, _SOURCE_GRAPPLE, actions)),
        }
        issues: list[str] = []
        for trigger, source_count in expected.items():
            runtime_count = sum(spec.trigger == trigger for spec in attack.conditional_attack_advantage)
            if source_count and runtime_count != 1:
                issues.append(f"conditional-attack-advantage-missing:{attack.id}:{trigger}")
            if not source_count and runtime_count:
                issues.append(f"conditional-attack-advantage-source-missing:{attack.id}:{trigger}")
        return issues
    except Exception:
        logger.exception("Failed conditional attack Advantage source audit for %s.", attack.id)
        raise
