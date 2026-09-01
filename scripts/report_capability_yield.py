from __future__ import annotations

from app.content.blocker_yield import build_blocker_signatures, single_family_yields
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.domain.catalog import CoverageStatus
from report_zero_engine_monsters import _source_blockers

_SIGNATURE_LIMIT = 25


def main() -> None:
    rows = load_monster_rows()
    monster_names = {str(row["name"]) for row in rows}
    ready_names = {
        card.name
        for card in build_monster_catalog()
        if card.coverage_status is CoverageStatus.RAW_READY
    }
    blockers_by_name: dict[str, list[str]] = {}
    for row in rows:
        name = str(row["name"])
        if name in ready_names:
            continue
        blockers = _source_blockers(row, monster_names)
        blockers_by_name[name] = blockers or ["unclassified-source-audit-gap"]

    signatures = build_blocker_signatures(blockers_by_name)
    singles = single_family_yields(signatures)
    print(
        "CAPABILITY_YIELD_BASELINE"
        f"\tready={len(ready_names)}\tblocked={len(blockers_by_name)}\tsignatures={len(signatures)}"
    )
    for blocker, names in sorted(singles.items(), key=lambda item: (-len(item[1]), item[0])):
        print(f"CAPABILITY_SINGLE_FAMILY\t{blocker}\t{len(names)}\t" + " | ".join(names))
    for index, (signature, names) in enumerate(signatures.items()):
        if index >= _SIGNATURE_LIMIT:
            break
        label = "+".join(signature) if signature else "none"
        print(f"CAPABILITY_SIGNATURE\t{len(names)}\t{label}\t" + " | ".join(names))


if __name__ == "__main__":
    main()
