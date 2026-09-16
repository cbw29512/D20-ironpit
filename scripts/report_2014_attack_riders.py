from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014

_FIELDS = (
    "conditional_damage",
    "conditional_attack_advantage",
    "on_hit_damage",
    "on_hit_save_effect",
    "on_hit_contested_movement",
    "ongoing_damage_effect",
    "control_effect",
    "resource_id",
    "breakable_restraint",
    "charge_profile",
    "forbid_target_grappled_by_self",
    "grapple_target_policy",
)
_EXPECTED_ATTACK_ONLY = 3


def _active(value: object, field: str) -> bool:
    if field == "grapple_target_policy":
        return value != "normal"
    return value not in (None, False, [], {})


def main() -> None:
    candidates = [
        monster for monster in load_monster_source_2014()
        if basic_blockers_2014(monster) == ("attack:complex",)
    ]
    print(f"2014 attack-complex-only: {len(candidates)}")
    for monster in candidates:
        for attack in monster.attacks:
            shape = {
                field: getattr(attack, field)
                for field in _FIELDS
                if _active(getattr(attack, field), field)
            }
            if shape:
                print("ATTACK_RIDER\t" + json.dumps({
                    "monster_id": monster.id,
                    "monster": monster.name,
                    "attack_id": attack.id,
                    "attack": attack.name,
                    "shape": shape,
                }, sort_keys=True, default=str))
    if len(candidates) != _EXPECTED_ATTACK_ONLY:
        raise RuntimeError(
            f"Expected {_EXPECTED_ATTACK_ONLY} attack-complex-only monsters, found {len(candidates)}"
        )


if __name__ == "__main__":
    main()
