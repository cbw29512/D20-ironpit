from app.combat.dice import FixedDiceProvider
from app.combat.start_turn import begin_turn_with_events
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


def _state():
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
        id="recharge-turn-creature",
        name="Recharge Turn Creature",
        archetype="Test",
        kind="monster",
        armor_class=10,
        max_hp=10,
        speed_ft=30,
        initiative_bonus=0,
        weapon_attack=WeaponAttack(
            id="test-strike", weapon=weapon, attack_bonus=0, damage_bonus=0,
        ),
        visual=VisualLoadout(armor="none", main_hand="none"),
        resources=[ResourceDefinition(id="breath", name="Breath Weapon", max_uses=1)],
        recharge_rules=[RechargeRule(resource_id="breath", minimum_roll=5)],
        source="Iron Pit start-turn recharge regression fixture",
    )
    return build_combatant_state(template)


def test_start_turn_emits_failed_recharge_audit_event() -> None:
    state = _state()
    state.resources[0].current_uses = 0
    events, sequence = begin_turn_with_events(7, 2, "monster-1", state, FixedDiceProvider([4]))
    assert sequence == 8
    assert len(events) == 1
    assert events[0].feature_id == "recharge:breath"
    assert events[0].resource_remaining == 0
    assert "rolls 4 for Recharge 5-6" in events[0].description
    assert state.action_available is True


def test_start_turn_restores_recharge_without_extra_action() -> None:
    state = _state()
    state.resources[0].current_uses = 0
    events, _ = begin_turn_with_events(1, 3, "monster-1", state, FixedDiceProvider([6]))
    assert events[0].resource_remaining == 1
    assert "breath recharges" in events[0].description
    assert state.resources[0].current_uses == 1
    assert state.action_available is True


def test_start_turn_skips_roll_when_recharge_is_available() -> None:
    state = _state()
    events, sequence = begin_turn_with_events(3, 1, "monster-1", state, FixedDiceProvider([1]))
    assert events == []
    assert sequence == 3
    assert state.resources[0].current_uses == 1
