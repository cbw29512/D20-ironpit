from __future__ import annotations

from app.content.monster_limited_use_source import limited_use_spec, parse_limited_use_names
from app.content.simple_monster_source_resources import attach_limited_use_resources


def test_per_day_attack_binds_to_finite_resource() -> None:
    row = {
        "name": "Test Fiend",
        "actions": "Flame Burst (2/Day). Ranged Attack Roll: +5, range 60/120 ft. Hit: 7 (1d8 + 3) Fire damage.",
    }
    attacks = [{"id": "flame-burst", "name": "Flame Burst (2/Day)"}]
    resources, fingerprints = attach_limited_use_resources(row, attacks, [])
    assert fingerprints == ["actions:Flame Burst (2/Day)"]
    assert resources == [{
        "id": "srd-test-fiend-actions-flame-burst-uses",
        "name": "Flame Burst",
        "max_uses": 2,
    }]
    assert attacks[0]["resource_id"] == resources[0]["id"]
    assert attacks[0]["resource_cost"] == 1


def test_recharge_save_uses_same_resource_abstraction() -> None:
    row = {
        "name": "Test Horror",
        "bonusActions": "Dread Glare (Recharge 5-6). Wisdom Saving Throw: DC 13, one creature within 30 feet. Failure: Frightened.",
    }
    saves = [{"id": "dread-glare", "name": "Dread Glare", "action_cost": "bonus_action"}]
    resources, fingerprints = attach_limited_use_resources(row, [], saves)
    assert fingerprints == ["bonusActions:Dread Glare (Recharge 5-6)"]
    assert resources[0]["max_uses"] == 1
    assert resources[0]["recharge"] == {"minimum": 5, "maximum": 6, "die_size": 6}
    assert saves[0]["resource_id"] == resources[0]["id"]
    assert saves[0]["resource_cost"] == 1


def test_limited_use_spec_normalizes_name_and_parameters() -> None:
    row = {"name": "Test", "actions": "Arc Flash (3/Day). Ranged Attack Roll: +4, range 30/60 ft. Hit: 5 (1d6 + 2) Lightning damage."}
    fingerprint = parse_limited_use_names(row)[0]
    spec = limited_use_spec(fingerprint)
    assert spec.base_name == "Arc Flash"
    assert spec.max_uses == 3
    assert spec.recharge_minimum is None
