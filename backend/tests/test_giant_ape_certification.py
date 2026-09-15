from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus


def test_giant_ape_runtime_reconciles_cleanly_to_srd_source() -> None:
    row = next(item for item in load_monster_rows() if item["name"] == "Giant Ape")
    template = next(item for item in build_arena_roster().monsters if item.name == "Giant Ape")

    assert audit_monster_source(template, row) == []


def test_giant_ape_catalog_is_raw_ready() -> None:
    card = next(item for item in build_monster_catalog() if item.name == "Giant Ape")

    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-giant-ape"
    assert card.blockers == []
