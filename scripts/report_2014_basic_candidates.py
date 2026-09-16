from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import (
    _ARENA_NEUTRAL_TRAITS,
    basic_blockers_2014,
)
from app.content.arena_neutral_bonus_actions import is_arena_neutral_bonus_action
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _unsupported_traits(monsters):
    return Counter(
        trait
        for monster in monsters
        for trait in monster.trait_names
        if trait not in _ARENA_NEUTRAL_TRAITS and not is_arena_neutral_bonus_action(trait)
    )


def main() -> None:
    monsters = load_monster_source_2014()
    ready = [monster for monster in monsters if not basic_blockers_2014(monster)]
    compiled = [compile_combatant(adapt_basic_monster_2014(monster)) for monster in ready]
    counts = Counter(
        blocker
        for monster in monsters
        for blocker in basic_blockers_2014(monster)
    )
    print(f"2014 basic candidates: {len(ready)}/{len(monsters)}")
    print(f"2014 basic candidates compiled: {len(compiled)}/{len(ready)}")
    print("Candidate names:")
    print(", ".join(monster.name for monster in ready))
    print("Blockers:")
    for blocker, count in counts.most_common():
        print(f"  {blocker}: {count}")
    print("Unsupported traits:")
    for trait, count in _unsupported_traits(monsters).most_common():
        print(f"  {count:3}  {trait}")
    if len(monsters) != 327:
        raise RuntimeError(f"Expected 327 source monsters, found {len(monsters)}")
    if len(ready) <= 4:
        raise RuntimeError("Bulk classifier did not improve on the four-monster MVP lane.")
    if len(compiled) != len(ready):
        raise RuntimeError("Not every admitted 2014 basic candidate compiled through the universal engine.")


if __name__ == "__main__":
    main()
