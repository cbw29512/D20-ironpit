from app.combat.charge import charge_profile
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_goat import build_goat
from app.domain.models import ChargeDamage, ChargeDefinition, DamageType


def test_charge_resolution_uses_attack_data_not_source_identity() -> None:
    template = build_goat().model_copy(deep=True)
    attack = template.weapon_attack.model_copy(update={
        "id": "homebrew-universal-runup-strike",
        "charge": ChargeDefinition(
            minimum_move_ft=15,
            replacement_damage=ChargeDamage(dice_count=2, dice_size=6, damage_type=DamageType.SLASHING),
        ),
    })
    template = template.model_copy(update={
        "weapon_attack": attack,
        "combat_traits": [],
        "name": "Unrelated Combatant",
    })
    attacker = build_combatant_state(template)
    defender = build_combatant_state(build_karnok_stoneward())

    resolved = charge_profile(attacker, defender, attack, 15)

    assert resolved is attack.charge
    assert resolved.replacement_damage is not None
    assert resolved.replacement_damage.damage_type is DamageType.SLASHING
    assert resolved.replacement_damage.dice_count == 2
