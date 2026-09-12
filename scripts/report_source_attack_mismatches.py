from __future__ import annotations

import logging
import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_general_action_fallback import is_general_rule_attack_id
from app.content.monster_source_audit import normalized
from app.content.roster import build_arena_roster
from app.domain.models import WeaponAttackKind

logger = logging.getLogger(__name__)

_MELEE_ATTACK_ROLL = re.compile(r"\bMelee\s+Attack Roll:", re.IGNORECASE)
_RANGED_ATTACK_ROLL = re.compile(r"\bRanged\s+Attack Roll:", re.IGNORECASE)
_COMBINED_ATTACK_ROLL = re.compile(r"\bMelee\s+or\s+Ranged\s+Attack Roll:", re.IGNORECASE)


def _source_attack_mode_count(actions: str) -> int:
    combined = len(_COMBINED_ATTACK_ROLL.findall(actions))
    standalone = _COMBINED_ATTACK_ROLL.sub("", actions)
    return (
        len(_MELEE_ATTACK_ROLL.findall(standalone))
        + len(_RANGED_ATTACK_ROLL.findall(standalone))
        + 2 * combined
    )


def _runtime_attack_mode_count(template: object) -> int:
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    source_bound = [attack for attack in attacks if not is_general_rule_attack_id(attack.id)]
    return sum(
        2 if attack.weapon.attack_kind is WeaponAttackKind.MELEE_OR_RANGED else 1
        for attack in source_bound
    )


def main() -> None:
    try:
        rows = {str(row["name"]): row for row in load_monster_rows()}
        templates = {monster.name: monster for monster in build_arena_roster().monsters}
        mismatches: list[tuple[str, int, int]] = []
        for name, template in sorted(templates.items()):
            row = rows.get(name)
            if row is None:
                continue
            source_count = _source_attack_mode_count(normalized(row.get("actions", "")))
            runtime_count = _runtime_attack_mode_count(template)
            if source_count != runtime_count:
                mismatches.append((name, source_count, runtime_count))
        print(f"SOURCE_ATTACK_COUNT_BASELINE\tmismatches={len(mismatches)}")
        for name, source_count, runtime_count in mismatches:
            print(
                "SOURCE_ATTACK_COUNT_MISMATCH"
                f"\t{name}\tsource={source_count}\truntime={runtime_count}"
            )
    except Exception:
        logger.exception("Failed to report source/runtime attack-count mismatches.")
        raise


if __name__ == "__main__":
    main()
