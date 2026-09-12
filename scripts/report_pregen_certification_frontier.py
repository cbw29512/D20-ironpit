from __future__ import annotations

from app.content.pregen_certification_queue import build_pregen_certification_frontier


def main() -> None:
    frontier = build_pregen_certification_frontier()
    ready = sum(candidate.ready for candidate in frontier)
    print(f"Pregen certification frontier: {len(frontier)} classes, {ready} ready without new engine work")
    print()
    for candidate in frontier:
        blockers = ", ".join(candidate.unsupported_features) or "none"
        status = "READY" if candidate.ready else f"BLOCKED x{candidate.blocker_count}"
        print(
            f"{candidate.class_id:10} L{candidate.next_level:>2} "
            f"(certified through L{candidate.certified_through:>2}) "
            f"{status}: {blockers}"
        )


if __name__ == "__main__":
    main()
