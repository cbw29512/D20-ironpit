from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.modifiers import ModifierKind


def _row(name: str):
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_ettin_compiles_entirely_from_existing_control_and_modifier_primitives() -> None:
    ettin = build_combatant_from_capabilities("srd-ettin")
    battleaxe, morningstar = ettin.weapon_attack, ettin.alternate_weapon_attacks[0]

    assert battleaxe.knocks_prone_max_size is not None
    assert battleaxe.knocks_prone_max_size.value == "large"
    assert len(morningstar.on_hit_modifier_effects) == 1
    rider = morningstar.on_hit_modifier_effects[0]
    assert rider.kind == "next-attack-disadvantage"
    assert rider.expires_at_end_of_target_turn is True
    assert audit_monster_source(ettin, _row("Ettin")) == []


def test_fire_giant_reuses_damage_push_and_next_attack_disadvantage_primitives() -> None:
    giant = build_combatant_from_capabilities("srd-fire-giant")
    flame_sword, hammer = giant.weapon_attack, giant.alternate_weapon_attacks[0]

    assert [(part.dice_count, part.dice_size, part.damage_type.value) for part in flame_sword.on_hit_damage] == [(3, 6, "fire")]
    assert [(part.dice_count, part.dice_size, part.damage_type.value) for part in hammer.on_hit_damage] == [(1, 8, "fire")]
    assert hammer.push_target_away_ft == 15
    assert len(hammer.on_hit_modifier_effects) == 1
    assert hammer.on_hit_modifier_effects[0].kind == "next-attack-disadvantage"
    assert audit_monster_source(giant, _row("Fire Giant")) == []
