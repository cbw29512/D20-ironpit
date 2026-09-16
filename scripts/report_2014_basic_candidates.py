from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014


def main() -> None:
    monsters = load_monster_source_2014()
    ready = [monster for monster in monsters if not basic_blockers_2014(monster)]
    counts = Counter(
        blocker
        for monster in monsters
        for blocker in basic_blockers_2014(monster)
    )
    print(f"2014 basic candidates: {len(ready)}/{len(monsters)}")
    print("Candidate names:")
    print(", ".join(monster.name for monster in ready))
    print("Blockers:")
    for blocker, count in counts.most_common():
        print(f"  {blocker}: {count}")
    if len(monsters) != 327:
        raise RuntimeError(f"Expected 327 source monsters, found {len(monsters)}")
    if len(ready) <= 4:
        raise RuntimeError("Bulk classifier did not improve on the four-monster MVP lane.")


if __name__ == "__main__":
    main()
