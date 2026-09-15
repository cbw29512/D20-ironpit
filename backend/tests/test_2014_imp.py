from app.content.monster_catalog_2014 import monster_by_id_2014


def test_imp_sting_compiles_malformed_srd_save_damage_as_structured_rider() -> None:
    imp = monster_by_id_2014("imp")
    attacks = [imp.weapon_attack, *imp.alternate_weapon_attacks]
    sting = next(attack for attack in attacks if attack.weapon.name.startswith("Sting"))
    effect = sting.on_hit_save_effect

    assert effect is not None
    assert effect.save_ability == "constitution"
    assert effect.dc == 11
    assert effect.damage_dice_count == 3
    assert effect.damage_dice_size == 6
    assert effect.damage_type == "poison"
    assert effect.success_damage == "half"
