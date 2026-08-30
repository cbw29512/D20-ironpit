from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus


def test_every_raw_ready_monster_reconciles_to_srd_5_2_1_source() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    runtime = {template.id: template for template in build_arena_roster().monsters}
    ready = [card for card in build_monster_catalog() if card.coverage_status is CoverageStatus.RAW_READY]

    assert len(ready) == 63
    for card in ready:
        assert card.runnable_template_id in runtime, f"Missing runtime template for {card.name}"
        issues = audit_monster_source(runtime[card.runnable_template_id], rows[card.name])
        assert issues == [], f"{card.name} does not reconcile to {card.source_reference}: {issues}"


def test_every_runtime_monster_is_publicly_certified() -> None:
    ready_ids = {
        card.runnable_template_id
        for card in build_monster_catalog()
        if card.coverage_status is CoverageStatus.RAW_READY
    }
    runtime_ids = {template.id for template in build_arena_roster().monsters}
    assert runtime_ids == ready_ids


def test_raw_ready_monsters_have_precise_srd_page_references() -> None:
    for card in build_monster_catalog():
        if card.coverage_status is CoverageStatus.RAW_READY:
            assert card.source_reference == f"SRD 5.2.1 p. {card.source_page}"
