from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.models import DamageType, WeaponAttackKind


def test_spy_capability_data_matches_srd_combat_math() -> None:
    try:
        spy = build_combatant_from_capabilities("srd-spy")
        attacks = {attack.weapon.name: attack for attack in [spy.weapon_attack, *spy.alternate_weapon_attacks]}

        crossbow = attacks["Hand Crossbow"]
        assert crossbow.weapon.attack_kind is WeaponAttackKind.RANGED
        assert (crossbow.attack_bonus, crossbow.weapon.dice_count, crossbow.weapon.dice_size, crossbow.damage_bonus) == (4, 1, 6, 2)
        assert (crossbow.weapon.normal_range_ft, crossbow.weapon.long_range_ft) == (30, 120)
        assert len(crossbow.on_hit_damage) == 1
        assert (crossbow.on_hit_damage[0].dice_count, crossbow.on_hit_damage[0].dice_size) == (2, 6)
        assert crossbow.on_hit_damage[0].damage_type is DamageType.POISON

        shortsword = attacks["Shortsword"]
        assert shortsword.weapon.attack_kind is WeaponAttackKind.MELEE
        assert (shortsword.attack_bonus, shortsword.weapon.dice_count, shortsword.weapon.dice_size, shortsword.damage_bonus) == (4, 1, 6, 2)
        assert len(shortsword.on_hit_damage) == 1
        assert shortsword.on_hit_damage[0].damage_type is DamageType.POISON
        assert spy.source_bonus_action_names == ["Cunning Action"]

        row = next(row for row in load_monster_rows() if row["name"] == "Spy")
        assert audit_monster_source(spy, row) == []
    except Exception as exc:
        raise AssertionError("Spy capability/source certification failed.") from exc
