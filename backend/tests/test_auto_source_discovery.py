from app.content.monster_catalog import load_monster_rows
from app.content.simple_monster_source_definitions import (
    audited_source_definition,
    discover_audited_source_definitions,
)


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_auto_source_discovery_is_fail_closed_on_full_source_audit() -> None:
    assert audited_source_definition(_row("Druid")) is not None
    assert audited_source_definition(_row("Fire Elemental")) is None


def test_auto_source_discovery_respects_existing_registry_ids() -> None:
    discovered = discover_audited_source_definitions({"srd-druid", "srd-dryad", "srd-imp"})
    assert {"srd-druid", "srd-dryad", "srd-imp"}.isdisjoint(discovered)
