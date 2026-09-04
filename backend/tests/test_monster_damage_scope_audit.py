from app.content.monster_catalog import load_monster_rows
from app.content.monster_damage_scope_audit import audit_monster_damage_scope


def test_every_canonical_monster_has_a_damage_scope_audit() -> None:
    rows = load_monster_rows()
    audits = [audit_monster_damage_scope(row) for row in rows]
    assert len(rows) == len(audits) == 330
    assert len({audit.monster_id for audit in audits}) == 330


def test_damage_scope_ignores_non_damage_riders_but_keeps_damage_families() -> None:
    row = {
        "id": "test-monster",
        "name": "Test Monster",
        "actions": (
            "Bite. Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Piercing damage, "
            "and the target is Grappled. Flame Burst (Recharge 5-6). Saving Throw: Dexterity DC 13. "
            "Failure: 14 (4d6) Fire damage. Success: Half damage."
        ),
        "traits": "Frightful Presence. Creatures can become Frightened.",
        "bonusActions": "",
        "reactions": "",
        "legendaryActions": "",
        "rawText": "Damage Resistances Fire",
    }
    audit = audit_monster_damage_scope(row)
    assert set(audit.families) >= {
        "attack-roll-damage",
        "save-damage",
        "limited-or-recharge-damage",
        "damage-defense",
    }
    assert all("condition" not in family for family in audit.families)
