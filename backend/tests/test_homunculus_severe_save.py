from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_capability_candidates import source_candidate_definitions
from app.domain.save_effects import ConditionEffectDefinition


def test_homunculus_bite_compiles_severe_failure_margin() -> None:
    row = next(row for row in load_monster_rows() if row["name"] == "Homunculus")
    candidates = source_candidate_definitions(set())
    definition = candidates["srd-homunculus"]
    bite = next(attack for attack in definition.attacks if attack.name == "Bite")
    rider = next(effect for effect in bite.effects if effect.kind == "saving-throw")

    assert rider.save_ability == "constitution"
    assert rider.dc == 12
    assert rider.severe_failure_margin == 5
    assert len(rider.failure_effects) == 1
    normal = rider.failure_effects[0]
    assert isinstance(normal, ConditionEffectDefinition)
    assert normal.condition == "poisoned"
    assert normal.expiry_timing == "source_turn_end"

    assert len(rider.severe_failure_effects) == 2
    poisoned, unconscious = rider.severe_failure_effects
    assert isinstance(poisoned, ConditionEffectDefinition)
    assert isinstance(unconscious, ConditionEffectDefinition)
    assert poisoned.condition == "poisoned"
    assert poisoned.duration_rounds == 10
    assert poisoned.expiry_timing == "source_turn_end"
    assert unconscious.condition == "unconscious"
    assert unconscious.duration_rounds == 10
    assert unconscious.expiry_timing == "source_turn_end"
    assert unconscious.ends_on_damage is True
