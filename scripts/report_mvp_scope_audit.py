from __future__ import annotations

from collections import Counter, defaultdict

from app.content.iron_pit_mvp_scope import direct_combat_math_reasons, movement_only_for_mvp
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.domain.catalog import CoverageStatus
from report_zero_engine_monsters import _source_blockers

_SECTIONS = ("traits", "actions", "bonusActions", "reactions", "legendaryActions")


def _section_scope(text: object) -> tuple[str, frozenset[str]]:
    source = str(text or "").strip()
    if not source:
        return "empty", frozenset()
    reasons = direct_combat_math_reasons(source)
    if reasons:
        return "direct", reasons
    if movement_only_for_mvp(source):
        return "movement-only", frozenset()
    return "deferred-nonmath", frozenset()


def main() -> None:
    rows = load_monster_rows()
    names = {str(row["name"]) for row in rows}
    ready = {
        card.name for card in build_monster_catalog()
        if card.coverage_status is CoverageStatus.RAW_READY
    }
    section_counts: dict[str, Counter[str]] = {section: Counter() for section in _SECTIONS}
    reason_counts: Counter[str] = Counter()
    current_blocker_counts: Counter[str] = Counter()
    movement_only_rows: defaultdict[str, list[str]] = defaultdict(list)
    deferred_rows: defaultdict[str, list[str]] = defaultdict(list)
    blocked_with_scope_only_sections: list[str] = []

    for row in rows:
        name = str(row["name"])
        current = set(_source_blockers(row, names))
        current_blocker_counts.update(current)
        has_direct = False
        has_nonempty = False
        for section in _SECTIONS:
            scope, reasons = _section_scope(row.get(section, ""))
            section_counts[section][scope] += 1
            if scope != "empty":
                has_nonempty = True
            if scope == "direct":
                has_direct = True
                reason_counts.update(reasons)
            elif scope == "movement-only":
                movement_only_rows[section].append(name)
            elif scope == "deferred-nonmath":
                deferred_rows[section].append(name)
        if current and has_nonempty and not has_direct:
            blocked_with_scope_only_sections.append(name)

    print(
        "IRON_PIT_MVP_SCOPE_AUDIT "
        f"catalog={len(rows)} ready={len(ready)} blocked={len(rows) - len(ready)} "
        f"blocked_scope_only_sections={len(blocked_with_scope_only_sections)}"
    )
    for section in _SECTIONS:
        counts = section_counts[section]
        print(
            f"MVP_SCOPE_SECTION section={section} direct={counts['direct']} "
            f"movement_only={counts['movement-only']} deferred_nonmath={counts['deferred-nonmath']} empty={counts['empty']}"
        )
    for reason, count in sorted(reason_counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"MVP_SCOPE_REASON reason={reason} count={count}")
    for blocker, count in sorted(current_blocker_counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"MVP_CURRENT_BLOCKER blocker={blocker} count={count}")
    for section, section_names in movement_only_rows.items():
        print(f"MVP_MOVEMENT_ONLY section={section} count={len(section_names)} names={';'.join(sorted(section_names))}")
    for section, section_names in deferred_rows.items():
        print(f"MVP_DEFERRED_NONMATH section={section} count={len(section_names)} names={';'.join(sorted(section_names))}")
    if blocked_with_scope_only_sections:
        print(
            "MVP_SCOPE_ONLY_BLOCKED "
            f"count={len(blocked_with_scope_only_sections)} names={';'.join(sorted(blocked_with_scope_only_sections))}"
        )


if __name__ == "__main__":
    main()
