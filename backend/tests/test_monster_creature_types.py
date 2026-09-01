from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_creature_types import base_creature_type, is_creature_type
from app.content.monster_source_audit import audit_monster_source


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_runtime_monsters_receive_exact_srd_creature_type() -> None:
    skeleton = build_combatant_from_capabilities("srd-skeleton")
    goblin = build_combatant_from_capabilities("srd-goblin-warrior")
    assert skeleton.creature_type == "Undead"
    assert goblin.creature_type == "Humanoid"
    assert is_creature_type(skeleton, "undead") is True
    assert is_creature_type(goblin, "undead") is False


def test_parenthetical_creature_type_preserves_source_and_matches_base_type() -> None:
    assert base_creature_type("Dragon (Chromatic)") == "dragon"
    assert base_creature_type("Humanoid (Goblin)") == "humanoid"
    assert base_creature_type(None) is None


def test_source_audit_fails_closed_when_creature_type_drifts() -> None:
    skeleton = build_combatant_from_capabilities("srd-skeleton")
    tampered = skeleton.model_copy(update={"creature_type": "Beast"})
    assert "creature-type-mismatch" in audit_monster_source(tampered, _row("Skeleton"))
