import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.recharge import resolve_recharge_checks
from app.combat.state import build_combatant_state
from app.domain.models import (
    CombatantTemplate,
    ResourceDefinition,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.recharge import RechargeRule


def _state(minimum_roll: int = 5):
    weapon = Weapon(
        id="test-strike",
        name="Test Strike",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=4,
        damage_type="bludgeoning",
        animation="melee",
    )
    template = CombatantTemplate(
        id="test-recharge-creature",
        name="Recharge Test Creature",
        archetype="Test",
        kind="monster",
        armor_class=10,
        max_hp=10,
        speed_ft=30,
        initiative_bonus=0,
        weapon_attack=WeaponAttack(
            id="test-strike",
            weapon=weapon,
            attack_bonus=0,
            damage_bonus=0,
        ),
        visual=VisualLoadout(armor="none", main_hand="none"),
        resources=[ResourceDefinition(id="breath", name="Breath Weapon", max_uses=1)],
        recharge_rules=[RechargeRule(resource_id="breath", minimum_roll=minimum_roll)],
        source="Iron Pit recharge regression fixture",
    )
    return build_combatant_state(template)


def test_recharge_does_not_roll_while_resource_is_available() -> None:
    state = _state()
    checks = resolve_recharge_checks(state, FixedDiceProvider([1]))
    assert checks == []
    assert state.resources[0].current_uses == 1


def test_failed_recharge_leaves_resource_expended() -> None:
    state = _state()
    state.resources[0].current_uses = 0
    checks = resolve_recharge_checks(state, FixedDiceProvider([4]))
    assert checks[0].roll == 4
    assert checks[0].restored is False
    assert checks[0].resource_remaining == 0


def test_successful_recharge_restores_resource_only() -> None:
    state = _state()
    state.resources[0].current_uses = 0
    state.action_available = False
    checks = resolve_recharge_checks(state, FixedDiceProvider([5]))
    assert checks[0].restored is True
    assert state.resources[0].current_uses == 1
    assert state.action_available is False


def test_recharge_six_requires_six() -> None:
    state = _state(6)
    state.resources[0].current_uses = 0
    checks = resolve_recharge_checks(state, FixedDiceProvider([5]))
    assert checks[0].restored is False


def test_missing_recharge_resource_fails_closed() -> None:
    state = _state()
    state.resources.clear()
    with pytest.raises(ValueError, match="not defined"):
        resolve_recharge_checks(state, FixedDiceProvider([6]))
