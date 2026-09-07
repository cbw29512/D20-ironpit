from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_mechanic_fingerprint import (
    mechanic_equivalence_fingerprint,
    source_ability_records,
)


def _row(name: str, actions: str) -> dict[str, object]:
    return {
        "name": name,
        "traits": "",
        "actions": actions,
        "bonusActions": "",
        "reactions": "",
        "legendaryActions": "",
        "rawText": actions,
    }


def test_equivalent_typed_damage_abilities_share_one_engine_family() -> None:
    poison = _row(
        "Poison Tester",
        "Venomous Tail. Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Piercing damage "
        "plus 3 (1d6) Poison damage. Constitution Saving Throw: DC 12. Failure: The target is Poisoned.",
    )
    cold = _row(
        "Cold Tester",
        "Frozen Claw. Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Slashing damage "
        "plus 3 (1d6) Cold damage. Constitution Saving Throw: DC 12. Failure: The target is Poisoned.",
    )

    poison_record = source_ability_records(poison)[0]
    cold_record = source_ability_records(cold)[0]

    assert poison_record["source_name"] == "Venomous Tail"
    assert cold_record["source_name"] == "Frozen Claw"
    assert poison_record["fingerprint"] != cold_record["fingerprint"]
    assert poison_record["equivalence_fingerprint"] == cold_record["equivalence_fingerprint"]


def test_conditions_remain_distinct_equivalence_families() -> None:
    poisoned = mechanic_equivalence_fingerprint(("attack-roll", "condition:poisoned", "damage", "damage:poison"))
    paralyzed = mechanic_equivalence_fingerprint(("attack-roll", "condition:paralyzed", "damage", "damage:poison"))

    assert poisoned != paralyzed


def test_unparsed_combat_source_is_visible_not_silently_dropped() -> None:
    malformed = _row("Malformed Tester", "this malformed source deals damage but has no reviewed heading")

    records = source_ability_records(malformed)

    assert len(records) == 1
    assert records[0]["parse_error"] is True
    assert "source-parse-error" in records[0]["mechanics"]


def test_all_srd_rows_can_be_scanned_into_registry_records() -> None:
    rows = load_monster_rows()
    records = [record for row in rows for record in source_ability_records(row)]

    assert len(rows) == 330
    assert records
    assert all(record["monster"] and record["source_name"] for record in records)
