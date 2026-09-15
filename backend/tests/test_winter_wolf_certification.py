from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus


def test_winter_wolf_runtime_reconciles_cleanly_to_srd_source() -> None:
    row = next(item for item in load_monster_rows() if item["name"] == "Winter Wolf")
    template = next(item for item in build_arena_roster().monsters if item.name == "Winter Wolf")

    assert audit_monster_source(template, row) == []


def test_winter_wolf_catalog_is_raw_ready() -> None:
    card = next(item for item in build_monster_catalog() if item.name == "Winter Wolf")

    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-winter-wolf"
    assert card.blockers == []
