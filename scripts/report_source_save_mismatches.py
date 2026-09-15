from __future__ import annotations

import logging

from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_save_count import source_action_save_count
from app.content.roster import build_arena_roster

logger = logging.getLogger(__name__)


def _runtime_save_count(template: object) -> int:
    action_count = sum(
        action.action_cost == "action"
        for action in template.saving_throw_actions
    )
    attack_count = sum(
        attack.on_hit_saving_throw is not None
        for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
    )
    return action_count + attack_count


def main() -> None:
    try:
        rows = {str(row["name"]): row for row in load_monster_rows()}
        templates = {monster.name: monster for monster in build_arena_roster().monsters}
        mismatches: list[tuple[str, int, int]] = []
        for name, template in sorted(templates.items()):
            row = rows.get(name)
            if row is None:
                continue
            source_count = source_action_save_count(str(row.get("actions", "")))
            runtime_count = _runtime_save_count(template)
            if source_count != runtime_count:
                mismatches.append((name, source_count, runtime_count))
        print(f"SOURCE_SAVE_COUNT_BASELINE\tmismatches={len(mismatches)}")
        for name, source_count, runtime_count in mismatches:
            print(
                "SOURCE_SAVE_COUNT_MISMATCH"
                f"\t{name}\tsource={source_count}\truntime={runtime_count}"
            )
    except Exception:
        logger.exception("Failed to report source/runtime save-count mismatches.")
        raise


if __name__ == "__main__":
    main()
