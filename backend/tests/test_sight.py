from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.sight import can_see_combatant
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.rogue import build_demo_rogue
from app.domain.models import (
    ActorVisibilityState,
    BattlefieldState,
    ConditionKind,
    RollMode,
)


def test_invisible_target_is_not_seen_in_supported_visibility_subset() -> None:
    observer = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_rogue())
    target.conditions.add(ConditionKind.INVISIBLE)

    assert can_see_combatant(observer, target) is False


def test_explicit_broken_line_of_sight_makes_target_unseen() -> None:
    observer = build_combatant_state(build_goblin_warrior())
    target = build_combatant_state(build_demo_rogue())
    battlefield = BattlefieldState(
        distance_ft=5,
        visibility_by_actor={
            target.template.id: ActorVisibilityState(enemy_line_of_sight=False)
        },
    )

    assert can_see_combatant(observer, target, battlefield) is False


def test_unseen_shortbow_attacker_at_five_feet_keeps_advantage() -> None:
    rogue = build_combatant_state(build_demo_rogue())
    goblin = build_combatant_state(build_goblin_warrior())
    rogue.conditions.add(ConditionKind.INVISIBLE)
    shortbow = rogue.template.alternate_weapon_attacks[0]

    event = resolve_attack(
        1,
        1,
        rogue,
        goblin,
        shortbow,
        5,
        FixedDiceProvider([6, 16, 4, 3]),
        battlefield=BattlefieldState(distance_ft=5),
    )

    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.ADVANTAGE
    assert event.attack_roll.selected_roll == 16
