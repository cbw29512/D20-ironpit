from app.content.monster_catalog_2014 import monster_by_id_2014


def _attack(monster_id: str, attack_name: str):
    monster = monster_by_id_2014(monster_id)
    attacks = [monster.weapon_attack, *monster.alternate_weapon_attacks]
    return next(attack for attack in attacks if attack.weapon.name == attack_name)


def test_pseudodragon_sting_uses_sleep_poison_escalation() -> None:
    attack = _attack("pseudodragon", "Sting")
    effect = attack.on_hit_save_effect

    assert effect is not None
    assert effect.save_ability == "constitution"
    assert effect.dc == 11
    assert effect.condition_id == "poisoned"
    assert effect.duration_rounds == 600
    assert effect.failure_margin_escalation is not None
    assert effect.failure_margin_escalation.margin == 5
    assert effect.failure_margin_escalation.additional_condition_ids == ["unconscious"]
    assert effect.failure_margin_escalation.ends_on_damage is True
    assert effect.failure_margin_escalation.allowed_removal_action_ids == ["wake-sleeper"]


def test_sprite_shortbow_uses_sleep_poison_escalation() -> None:
    attack = _attack("sprite", "Shortbow")
    effect = attack.on_hit_save_effect

    assert effect is not None
    assert effect.save_ability == "constitution"
    assert effect.dc == 10
    assert effect.condition_id == "poisoned"
    assert effect.duration_rounds == 10
    assert effect.failure_margin_escalation is not None
    assert effect.failure_margin_escalation.margin == 5
    assert effect.failure_margin_escalation.additional_condition_ids == ["unconscious"]
    assert effect.failure_margin_escalation.ends_on_damage is True
    assert effect.failure_margin_escalation.allowed_removal_action_ids == ["wake-sleeper"]
