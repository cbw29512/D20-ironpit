from app.combat.dice import FixedDiceProvider
from app.combat.start_turn import begin_turn_with_events
from app.combat.state import build_combatant_state
from app.combat.zero_hp import restore_hit_points
from app.domain.models import (
    CombatantTemplate,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.targeting_overrides import TurnStartTargetingOverrideRule


def _template() -> CombatantTemplate:
    weapon = Weapon(
        id="slam",
        name="Slam",
        attack_kind=WeaponAttackKind.MELEE,
        dice_count=1,
        dice_size=6,
        damage_type="bludgeoning",
        animation="melee",
    )
    return CombatantTemplate(
        id="test-override",
        name="Test Override",
        archetype="Test",
        kind="monster",
        armor_class=10,
        max_hp=100,
        speed_ft=30,
        initiative_bonus=0,
        weapon_attack=WeaponAttack(
            id="slam",
            weapon=weapon,
            attack_bonus=5,
            damage_bonus=3,
        ),
        turn_start_targeting_overrides=[TurnStartTargetingOverrideRule(
            source_id="test-turn-start-override",
            source_name="Test Override",
            max_current_hp=40,
            die_size=6,
            minimum_roll=6,
            ends_on_full_hp=True,
        )],
        visual=VisualLoadout(armor="none", main_hand="slam"),
        source="test",
    )


def test_turn_start_roll_activates_once() -> None:
    state = build_combatant_state(_template())
    state.current_hp = 40

    events, sequence = begin_turn_with_events(
        3, 2, "actor", state, FixedDiceProvider([6])
    )
    assert sequence == 4
    assert events[0].feature_id == "test-turn-start-override"
    assert events[0].feature_roll.total == 6
    assert state.active_targeting_override_ids == ["test-turn-start-override"]

    events, sequence = begin_turn_with_events(
        4, 3, "actor", state, FixedDiceProvider([1])
    )
    assert events == []
    assert sequence == 4
    assert state.active_targeting_override_ids == ["test-turn-start-override"]


def test_failed_turn_start_roll_does_not_activate() -> None:
    state = build_combatant_state(_template())
    state.current_hp = 40

    events, _ = begin_turn_with_events(
        1, 1, "actor", state, FixedDiceProvider([5])
    )

    assert events[0].feature_roll.total == 5
    assert state.active_targeting_override_ids == []


def test_full_hp_healing_ends_active_override() -> None:
    state = build_combatant_state(_template())
    state.current_hp = 99
    state.active_targeting_override_ids = ["test-turn-start-override"]

    assert restore_hit_points(state, 1) == 1
    assert state.current_hp == 100
    assert state.active_targeting_override_ids == []
