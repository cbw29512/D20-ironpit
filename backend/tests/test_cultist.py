from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.monsters_zero_engine import build_zero_engine_monsters
from app.domain.models import DamageType


def test_cultist_ritual_sickle_matches_srd_fixed_necrotic_rider() -> None:
    cultist = next(template for template in build_zero_engine_monsters() if template.name == "Cultist")
    attack = cultist.weapon_attack
    assert attack.weapon.name == "Ritual Sickle"
    assert (attack.attack_bonus, attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (3, 1, 4, 1)
    assert attack.weapon.damage_type is DamageType.SLASHING
    assert len(attack.on_hit_damage) == 1
    rider = attack.on_hit_damage[0]
    assert (rider.dice_count, rider.damage_bonus, rider.damage_type) == (0, 1, DamageType.NECROTIC)

    row = next(row for row in load_monster_rows() if row["name"] == "Cultist")
    assert audit_monster_source(cultist, row) == []
