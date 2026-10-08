from app.combat.dice import FixedDiceProvider
from app.combat.start_turn import begin_turn_with_events
from app.combat.state import build_combatant_state
from app.combat.zero_hp import restore_hit_points
from app.domain.models import CombatantTemplate, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.turn_start_effects import TurnStartPersistentEffectRule


def _template() -> CombatantTemplate:
    weapon = Weapon(
        id="slam", name="Slam", attack_kind=WeaponAttackKind.MELEE,
        dice_count=1, dice_size=6, damage_type="bludgeoning", animation="melee",
    )
    return CombatantTemplate(
        id="test-construct", name="Test Construct", archetype="Test",
        kind="monster", armor_class=10, max_hp=100, speed_ft=30, initiative_bonus=0,
        weapon_attack=WeaponAttack(id="slam", weapon=weapon, attack_bonus=5, damage_bonus=3),
        turn_start_persistent_effects=[TurnStartPersistentEffectRule(
            source_id="test-threshold-state",
            source_name="Threshold State",
            effect_id="test-threshold-state-active",
            max_current_hp=40,
            die_size=6,
            minimum_roll=6,
        )],
        visual=VisualLoadout(armor="none", main_hand="slam"),
        source="test",
    )


def test_turn_start_roll_activates_once_and_full_hp_healing_ends_effect() -> None:
    state = build_combatant_state(_template())
    state.current_hp = 40

    events, sequence = begin_turn_with_events(3, 2, "construct", state, FixedDiceProvider([6]))
    assert sequence == 4
    assert events[0].feature_id == "test-threshold-state"
    assert events[0].feature_roll.total == 6
    assert state.active_effect_ids == ["test-threshold-state-active"]

    events, sequence = begin_turn_with_events(4, 3, "construct", state, FixedDiceProvider([1]))
    assert events == []
    assert sequence == 4

    state.current_hp = 99
    assert restore_hit_points(state, 1) == 1
    assert "test-threshold-state-active" not in state.active_effect_ids


def test_failed_or_above_threshold_turn_start_does_not_activate_effect() -> None:
    state = build_combatant_state(_template())
    state.current_hp = 40
    events, _ = begin_turn_with_events(1, 1, "construct", state, FixedDiceProvider([5]))
    assert events[0].feature_roll.total == 5
    assert "test-threshold-state-active" not in state.active_effect_ids

    state.current_hp = 41
    events, sequence = begin_turn_with_events(2, 2, "construct", state, FixedDiceProvider([6]))
    assert events == []
    assert sequence == 2
