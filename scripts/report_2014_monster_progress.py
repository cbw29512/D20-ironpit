from __future__ import annotations

from collections import Counter, defaultdict

from app.content.monster_catalog_2014 import load_catalog_2014, unsupported_mechanics_2014


def _attack_detail_family(text: str | None) -> str:
    value = (text or "").lower()
    tags: list[str] = []
    if "saving throw" in value or " dc " in f" {value} ": tags.append("save")
    if "grappled" in value or "escape dc" in value: tags.append("grapple")
    if "restrained" in value: tags.append("restrained")
    if "poison" in value: tags.append("poison")
    for condition in ("prone", "frightened", "paralyzed", "unconscious", "blinded", "stunned"):
        if condition in value: tags.append(condition)
    if "start of" in value or "each turn" in value or "until" in value: tags.append("ongoing")
    if "swallowed" in value or "swallow" in value: tags.append("swallow")
    return "+".join(dict.fromkeys(tags)) if tags else "other"


def main() -> int:
    monsters = load_catalog_2014()
    family_counts: Counter[str] = Counter()
    exact_counts: Counter[str] = Counter()
    exact_monsters: dict[str, set[str]] = defaultdict(set)
    rider_counts: Counter[str] = Counter()
    rider_monsters: dict[str, set[str]] = defaultdict(set)
    runnable: list[str] = []

    for monster in monsters:
        blockers = unsupported_mechanics_2014(monster)
        if not blockers:
            runnable.append(monster.name)
            continue
        for attack in monster.attacks:
            if not attack.source_complete:
                family = _attack_detail_family(attack.unsupported_text)
                key = f"{attack.name}:{family}"
                rider_counts[key] += 1
                rider_monsters[key].add(monster.name)
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
        print(f"- {blocker}: {len(names)} monsters / {exact_counts[blocker]} references ({examples})")

    print("\nUnresolved attack rider families:")
    ranked_riders = sorted(rider_counts, key=lambda key: (-len(rider_monsters[key]), -rider_counts[key], key))
    for key in ranked_riders[:30]:
        names = sorted(rider_monsters[key])
        print(f"- {key}: {len(names)} monsters / {rider_counts[key]} references ({', '.join(names[:5])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
