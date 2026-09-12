from __future__ import annotations

from collections import Counter, defaultdict

from app.content.monster_catalog_2014 import load_catalog_2014, unsupported_mechanics_2014


def main() -> int:
    monsters = load_catalog_2014()
    family_counts: Counter[str] = Counter()
    exact_counts: Counter[str] = Counter()
    exact_monsters: dict[str, set[str]] = defaultdict(set)
    runnable: list[str] = []

    for monster in monsters:
        blockers = unsupported_mechanics_2014(monster)
        if not blockers:
            runnable.append(monster.name)
            continue
        for blocker in blockers:
            family = blocker.split(":", 1)[0]
            family_counts[family] += 1
            exact_counts[blocker] += 1
            exact_monsters[blocker].add(monster.name)

    print(f"2014 catalog monsters: {len(monsters)}")
    print(f"Conservatively engine-compatible now: {len(runnable)}")
    print(f"Blocked by unresolved mechanics: {len(monsters) - len(runnable)}")
    print("\nBlocker families:")
    for family, count in family_counts.most_common():
        print(f"- {family}: {count} references")

    print("\nHighest-yield exact blockers:")
    ranked = sorted(
        exact_counts,
        key=lambda blocker: (-len(exact_monsters[blocker]), -exact_counts[blocker], blocker),
    )
    for blocker in ranked[:30]:
        names = sorted(exact_monsters[blocker])
        examples = ", ".join(names[:5])
        print(
            f"- {blocker}: {len(names)} monsters / {exact_counts[blocker]} references"
            f" ({examples})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
