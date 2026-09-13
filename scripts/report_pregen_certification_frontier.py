from __future__ import annotations

from app.content.canonical_pregen_spell_gaps import first_spell_package_gap_by_class
from app.content.pregen_blocker_yield import build_pregen_blocker_yields
from app.content.pregen_certification_queue import build_pregen_certification_frontier


def main() -> None:
    frontier = build_pregen_certification_frontier()
    ready = sum(candidate.ready for candidate in frontier)
    print(f"Pregen certification frontier: {len(frontier)} classes, {ready} ready without new engine work")
    print()
    for candidate in frontier:
        blockers = ", ".join(candidate.blockers) or "none"
        status = "READY" if candidate.ready else f"BLOCKED x{candidate.blocker_count}"
        print(
            f"{candidate.class_id:10} L{candidate.next_level:>2} "
            f"(certified through L{candidate.certified_through:>2}) "
            f"{status}: {blockers}"
        )

    print("\nFirst incomplete canonical spell package by caster")
    for class_id, gap in first_spell_package_gap_by_class().items():
        status = "complete through L20" if gap is None else f"first gap L{gap.level}: {gap.reason}"
        print(f"{class_id:10} {status}")

    print("\nHighest-yield unsupported hero mechanics")
    for item in build_pregen_blocker_yields()[:20]:
        frontier_classes = ",".join(item.frontier_classes) or "-"
        print(
            f"{item.feature_id:36} frontier={item.frontier_count:>2} "
            f"remaining_snapshots={item.remaining_snapshots:>3} classes={frontier_classes}"
        )


if __name__ == "__main__":
    main()
