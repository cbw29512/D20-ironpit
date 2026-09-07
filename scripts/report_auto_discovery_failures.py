from __future__ import annotations

from app.content.monster_auto_discovery_diagnostics import auto_discovery_failure
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.domain.catalog import CoverageStatus


def main() -> None:
    blocked = {
        card.name for card in build_monster_catalog()
        if card.coverage_status is not CoverageStatus.RAW_READY
    }
    rows = {str(row["name"]): row for row in load_monster_rows()}
    for name in sorted(blocked):
        stage, detail = auto_discovery_failure(rows[name])
        print(f"AUTO_DISCOVERY_FAILURE\t{stage}\t{name}\t{detail}")


if __name__ == "__main__":
    main()
