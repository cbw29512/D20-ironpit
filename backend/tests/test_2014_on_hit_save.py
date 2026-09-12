from app.combat.dice import FixedDiceProvider
from app.combat.on_hit_saves import resolve_on_hit_save
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.domain.on_hit_saves import OnHitSaveEffect
from app.domain.weapons import Weapon, WeaponAttack, WeaponAttackKind


def _bite() -> WeaponAttack:
    return WeaponAttack(
        id="test-bite",
        weapon=Weapon(
            id="test-bite",
            name="Bite",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=6,
            damage_type="piercing",
            animation="melee",
        ),
        attack_bonus=5,
        damage_bonus=3,
        on_hit_save_effect=OnHitSaveEffect(
            save_ability="strength",
            dc=20,
            condition_id="prone",
        ),
    )


def test_on_hit_save_condition_applies_only_on_failed_save() -> None:
    failed = build_combatant_state(build_demo_fighter())
    failure = resolve_on_hit_save(failed, _bite(), FixedDiceProvider([1]))
    assert failure.save_succeeded is False
    assert failure.applied_condition == "prone"
    assert "prone" in failed.active_effect_ids

    succeeded = build_combatant_state(build_demo_fighter())
    success = resolve_on_hit_save(succeeded, _bite(), FixedDiceProvider([20]))
    assert success.save_succeeded is True
    assert success.applied_condition is None
    assert "prone" not in succeeded.active_effect_ids
