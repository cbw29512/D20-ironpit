from __future__ import annotations

from app.content.monster_aura_source import source_start_turn_condition_auras
from app.content.monster_source_attack_riders import parse_attack_riders


def _hit_save(text: str):
    effects = parse_attack_riders(text)
    saves = [effect for effect in effects if effect.kind == "saving-throw"]
    assert len(saves) == 1
    return saves[0]


def test_ghast_style_hit_save_excludes_undead() -> None:
    rider = _hit_save(
        "If the target is a non-Undead creature, it is subjected to the following effect. "
        "Constitution Saving Throw: DC 10. Failure: The target has the Paralyzed condition until the end of its next turn."
    )
    assert rider.target_filter.excluded_creature_types == ["undead"]
    assert rider.target_filter.excluded_tags == []
    assert rider.failure_effects[0].condition == "paralyzed"


def test_ghoul_style_hit_save_excludes_undead_and_elf() -> None:
    rider = _hit_save(
        "If the target is a creature that isn't an Undead or elf, it is subjected to the following effect. "
        "Constitution Saving Throw: DC 10. Failure: The target has the Paralyzed condition until the end of its next turn."
    )
    assert rider.target_filter.excluded_creature_types == ["undead"]
    assert rider.target_filter.excluded_tags == ["elf"]
    assert not rider.target_filter.allows("undead", [])
    assert not rider.target_filter.allows("humanoid", ["elf"])
    assert rider.target_filter.allows("humanoid", ["orc"])


def test_ghast_stench_success_grants_source_specific_immunity() -> None:
    auras = source_start_turn_condition_auras("Ghast")
    assert len(auras) == 1
    aura = auras[0]
    assert aura.name == "Stench"
    assert aura.condition == "poisoned"
    assert aura.dc == 10
    assert aura.success_grants_source_immunity is True
