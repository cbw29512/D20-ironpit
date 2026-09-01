from app.content.capability_registry import build_combatant_from_capabilities, build_monster_templates_from_capabilities
from app.content.monster_creature_types import base_creature_type, creature_type_matches_source, is_creature_type


def test_runtime_monsters_receive_exact_srd_creature_type() -> None:
    skeleton = build_combatant_from_capabilities("srd-skeleton")
    goblin = build_combatant_from_capabilities("srd-goblin-warrior")
    assert skeleton.creature_type == "Undead"
    assert goblin.creature_type == "Fey (Goblinoid)"
    assert is_creature_type(skeleton, "undead") is True
    assert is_creature_type(goblin, "undead") is False
    assert is_creature_type(goblin, "fey") is True


def test_every_compiled_runtime_monster_matches_canonical_source_type() -> None:
    monsters = build_monster_templates_from_capabilities()
    assert monsters
    assert all(creature_type_matches_source(monster) for monster in monsters)
    assert all(monster.creature_type for monster in monsters)


def test_parenthetical_creature_type_preserves_source_and_matches_base_type() -> None:
    assert base_creature_type("Dragon (Chromatic)") == "dragon"
    assert base_creature_type("Fey (Goblinoid)") == "fey"
    assert base_creature_type(None) is None


def test_creature_type_source_parity_fails_closed_when_runtime_is_tampered() -> None:
    skeleton = build_combatant_from_capabilities("srd-skeleton")
    tampered = skeleton.model_copy(update={"creature_type": "Beast"})
    assert creature_type_matches_source(tampered) is False
