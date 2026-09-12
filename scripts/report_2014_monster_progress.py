from __future__ import annotations

from collections import Counter, defaultdict

from app.content.monster_catalog_2014 import load_catalog_2014, unsupported_mechanics_2014


def main() -> int:
    monsters = load_catalog_2014()
    blocker_counts: Counter[str] = Counter()
    blocker_monsters: dict[str, list[str]] = defaultdict(list)
    runnable: list[str] = []
    for monster in monsters:
        blockers = unsupported_mechanics_2014(monster)
        if not blockers:
            runnable.append(monster.name)
            continue
        for blocker in blockers:
            family = blocker.split(":", 1)[0]
            blocker_counts[family] += 1
            blocker_monsters[family].append(monster.name)

    print(f"2014 catalog monsters: {len(monsters)}")
    print(f"Basic engine-compatible now: {len(runnable)}")
    print(f"Blocked by unresolved mechanics: {len(monsters) - len(runnable)}")
    print("\nBlocker families:")
    for family, count in blocker_counts.most_common():
        examples = ", ".join(blocker_monsters[family][:5])
        print(f"- {family}: {count} monster references ({examples})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
