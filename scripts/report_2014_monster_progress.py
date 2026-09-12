from __future__ import annotations

import html
import re
from collections import Counter, defaultdict

from app.content.monster_catalog_2014 import load_catalog_2014, unsupported_mechanics_2014


def _attack_detail_family(text: str | None) -> str:
    value = (text or "").lower(); tags: list[str] = []
    if "saving throw" in value or " dc " in f" {value} ": tags.append("save")
    if "grappled" in value or "escape dc" in value: tags.append("grapple")
    if "restrained" in value: tags.append("restrained")
    if "poison" in value: tags.append("poison")
    for condition in ("prone", "frightened", "paralyzed", "unconscious", "blinded", "stunned"):
        if condition in value: tags.append(condition)
    if "start of" in value or "each turn" in value or "until" in value: tags.append("ongoing")
    if "swallowed" in value or "swallow" in value: tags.append("swallow")
    return "+".join(dict.fromkeys(tags)) if tags else "other"


def _multiattack_text(source_actions: str | None) -> str:
    for paragraph in re.findall(r"<p>(.*?)</p>", source_actions or "", re.I | re.S):
        if re.search(r"<strong>\s*Multiattack", paragraph, re.I):
            text = re.sub(r"<[^>]+>", " ", paragraph)
            return re.sub(r"\s+", " ", html.unescape(text)).strip()
    return ""


def main() -> int:
    monsters = load_catalog_2014(); family_counts: Counter[str] = Counter(); exact_counts: Counter[str] = Counter()
    exact_monsters: dict[str, set[str]] = defaultdict(set); rider_counts: Counter[str] = Counter()
    immediate_unlocks: dict[str, set[str]] = defaultdict(set); blocker_count_histogram: Counter[int] = Counter()
    rider_monsters: dict[str, set[str]] = defaultdict(set); rider_examples: dict[str, str] = {}; runnable: list[str] = []
    multiattack_examples: list[tuple[str, str]] = []
    for monster in monsters:
        blockers = unsupported_mechanics_2014(monster)
        if not blockers: runnable.append(monster.name); continue
        unique_blockers = set(blockers); blocker_count_histogram[len(unique_blockers)] += 1
        if len(unique_blockers) == 1:
            immediate_unlocks[next(iter(unique_blockers))].add(monster.name)
        if "action:Multiattack" in blockers:
            multiattack_examples.append((monster.name, _multiattack_text(monster.source_actions)))
        for attack in monster.attacks:
            if not attack.source_complete:
                family = _attack_detail_family(attack.unsupported_text); key = f"{attack.name}:{family}"
                rider_counts[key] += 1; rider_monsters[key].add(monster.name)
                rider_examples.setdefault(key, attack.unsupported_text or "")
        for blocker in blockers:
            family = blocker.split(":", 1)[0]; family_counts[family] += 1; exact_counts[blocker] += 1; exact_monsters[blocker].add(monster.name)

    print(f"2014 catalog monsters: {len(monsters)}")
    print(f"Conservatively engine-compatible now: {len(runnable)}")
    print(f"Blocked by unresolved mechanics: {len(monsters) - len(runnable)}")
    print("\nBlocker families:")
    for family, count in family_counts.most_common(): print(f"- {family}: {count} references")

    print("\nImmediate certification yield (sole remaining blocker):")
    ranked_unlocks = sorted(immediate_unlocks, key=lambda blocker: (-len(immediate_unlocks[blocker]), blocker))
    if not ranked_unlocks:
        print("- none")
    for blocker in ranked_unlocks[:30]:
        names = sorted(immediate_unlocks[blocker])
        print(f"- {blocker}: +{len(names)} monsters ({', '.join(names[:8])})")
    print("\nBlocked-monster distance to certification:")
    for count in sorted(blocker_count_histogram):
        print(f"- {count} unique blocker(s): {blocker_count_histogram[count]} monsters")

    print("\nHighest-yield exact blockers:")
    ranked = sorted(exact_counts, key=lambda blocker: (-len(exact_monsters[blocker]), -exact_counts[blocker], blocker))
    for blocker in ranked[:30]:
        names = sorted(exact_monsters[blocker]); examples = ", ".join(names[:5])
        print(f"- {blocker}: {len(names)} monsters / {exact_counts[blocker]} references ({examples})")

    if multiattack_examples:
        print("\nUnresolved Multiattack source shapes:")
        for name, text in multiattack_examples[:20]: print(f"- {name}: {text[:260]}")

    print("\nUnresolved attack rider families:")
    ranked_riders = sorted(rider_counts, key=lambda key: (-len(rider_monsters[key]), -rider_counts[key], key))
    for key in ranked_riders[:30]:
        names = sorted(rider_monsters[key]); sample = rider_examples[key].replace("\n", " ")[:220]
        print(f"- {key}: {len(names)} monsters / {rider_counts[key]} references ({', '.join(names[:5])})")
        print(f"  residual: {sample}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
