from __future__ import annotations

from collections import defaultdict

from app.content.blocker_yield import build_blocker_signatures, single_family_yields
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_trait_source_audit import parse_trait_names
from app.domain.catalog import CoverageStatus
from report_zero_engine_monsters import _ALLOWED_TRAITS, _source_blockers

_SIGNATURE_LIMIT = 25


def _trait_heading_yields(rows_by_name: dict[str, dict[str, object]], names: list[str]) -> dict[str, list[str]]:
    yields: dict[str, list[str]] = defaultdict(list)
    for name in names:
        traits = parse_trait_names(rows_by_name[name].get("traits", ""))
        unsupported = [trait for trait in traits if trait not in _ALLOWED_TRAITS]
        if not unsupported:
            raise RuntimeError(f"Trait-only blocker {name!r} has no unsupported trait heading.")
        for trait in unsupported:
            yields[trait].append(name)
    return {
        trait: sorted(monsters)
        for trait, monsters in sorted(yields.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def main() -> None:
    rows = load_monster_rows()
    rows_by_name = {str(row["name"]): row for row in rows}
    monster_names = set(rows_by_name)
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
    for trait, names in _trait_heading_yields(rows_by_name, singles.get("trait", [])).items():
        print(f"CAPABILITY_TRAIT_HEADING\t{trait}\t{len(names)}\t" + " | ".join(names))
    for index, (signature, names) in enumerate(signatures.items()):
        if index >= _SIGNATURE_LIMIT:
            break
        label = "+".join(signature) if signature else "none"
        print(f"CAPABILITY_SIGNATURE\t{len(names)}\t{label}\t" + " | ".join(names))


if __name__ == "__main__":
    main()
