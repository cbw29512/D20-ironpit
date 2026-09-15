from __future__ import annotations

from app.content.monster_catalog import load_monster_rows
from app.content.monster_limited_use_source_audit import limited_use_issues, parse_limited_use_names
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.combatants import RechargeRule


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def test_recharge_marker_is_fingerprinted_with_source_section() -> None:
    assert parse_limited_use_names(_row("Gold Dragon Wyrmling")) == [
        "actions:Fire Breath (Recharge 5-6)",
    ]


def test_per_day_marker_is_fingerprinted_with_source_section() -> None:
    assert parse_limited_use_names(_row("Gnoll Warrior")) == ["bonusActions:Rampage (1/Day)"]


def test_current_saber_tooth_has_no_limited_use_feature() -> None:
    saber = _monster("Saber-Toothed Tiger")
    assert saber.source_limited_use_names == []
    assert limited_use_issues(saber, _row("Saber-Toothed Tiger")) == []


def test_unimplemented_recharge_economy_fails_closed() -> None:
    wolf = _monster("Wolf")
    row = dict(_row("Wolf"))
    row["actions"] = "Howl (Recharge 5-6). Wisdom Saving Throw: DC 12. Failure: Frightened."
    expected = ["actions:Howl (Recharge 5-6)"]
    drifted = wolf.model_copy(update={"source_limited_use_names": expected})
    issues = limited_use_issues(drifted, row)
    assert "uncertified-limited-use:actions-howl-recharge-5-6" in issues


def test_source_derived_ape_recharge_is_bound_and_certified() -> None:
    ape = _monster("Ape")
    row = _row("Ape")
    rock = next(attack for attack in ape.alternate_weapon_attacks if attack.weapon.name == "Rock")

    assert ape.source_limited_use_names == ["actions:Rock (Recharge 6)"]
    assert rock.resource_id == "ape-rock-recharge"
    assert ape.attack_action is not None
    assert [slot.attack_ids for slot in ape.attack_action.slots] == [["ape-fist"], ["ape-fist"]]
    assert limited_use_issues(ape, row) == []
    assert audit_monster_source(ape, row) == []


def test_recharge_threshold_mismatch_still_fails_closed() -> None:
    ape = _monster("Ape")
    definition = ape.resources[0]
    wrong_rule = RechargeRule(minimum_roll=5)
    drifted = ape.model_copy(update={
        "resources": [definition.model_copy(update={"recharge": wrong_rule})],
    })

    assert "uncertified-limited-use:actions-rock-recharge-6" in limited_use_issues(drifted, _row("Ape"))


def test_limited_use_fingerprint_drift_is_detected() -> None:
    wolf = _monster("Wolf").model_copy(update={"source_limited_use_names": ["actions:Howl (Recharge 5-6)"]})
    assert "source-limited-use-fingerprint-mismatch" in limited_use_issues(wolf, _row("Wolf"))
