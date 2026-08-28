from app.combat.battle_start import resolve_battle_start
from app.combat.dice import FixedDiceProvider
from app.combat.initiative import roll_initiative_order
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import (
    ActorVisibilityState,
    BattlefieldState,
    ConditionKind,
    EncounterSetup,
    PrecombatActorPlan,
    RollMode,
)


def build_stealth_ambusher():
    template = build_demo_fighter().model_copy(deep=True)
    template.id = "stealth-ambusher"
    template.name = "Stealth Ambusher"
    template.skill_bonuses["stealth"] = 7
    return build_combatant_state(template)


def concealed_battlefield(actor_id: str) -> BattlefieldState:
    return BattlefieldState(
        starting_distance_ft=30,
        distance_ft=30,
        visibility_by_actor={
            actor_id: ActorVisibilityState(
                heavily_obscured=True,
                enemy_line_of_sight=False,
            )
        },
    )


def test_precombat_hide_can_create_surprise_without_spending_combat_actions() -> None:
    ambusher = build_stealth_ambusher()
    target = build_combatant_state(build_goblin_warrior())
    setup = EncounterSetup(
        plans_by_actor={
            ambusher.template.id: PrecombatActorPlan(
                attempt_hide=True,
                ambush_target_ids={target.template.id},
            )
        }
    )

    events, order, next_sequence = resolve_battle_start(
        [ambusher, target],
        concealed_battlefield(ambusher.template.id),
        FixedDiceProvider([12, 6, 17, 18, 4]),
        setup,
    )

    assert [event.event_type for event in events] == ["hide", "initiative", "initiative"]
    assert events[0].feature_id == "precombat-hide"
    assert ambusher.hidden is True
    assert ambusher.action_available is True
    assert ambusher.bonus_action_available is True
    ambusher_init = next(event for event in events if event.actor_id == ambusher.template.id and event.event_type == "initiative")
    target_init = next(event for event in events if event.actor_id == target.template.id and event.event_type == "initiative")
    assert ambusher_init.attack_roll is not None
    assert ambusher_init.attack_roll.mode is RollMode.ADVANTAGE
    assert target_init.attack_roll is not None
    assert target_init.attack_roll.mode is RollMode.DISADVANTAGE
    assert target_init.feature_id == "surprise"
    assert order[0] is ambusher
    assert next_sequence == 4


def test_failed_precombat_hide_does_not_surprise_target() -> None:
    ambusher = build_stealth_ambusher()
    target = build_combatant_state(build_goblin_warrior())
    setup = EncounterSetup(
        plans_by_actor={
            ambusher.template.id: PrecombatActorPlan(
                attempt_hide=True,
                ambush_target_ids={target.template.id},
            )
        }
    )

    events, _, _ = resolve_battle_start(
        [ambusher, target],
        concealed_battlefield(ambusher.template.id),
        FixedDiceProvider([3, 10, 11]),
        setup,
    )

    assert ambusher.hidden is False
    target_init = next(event for event in events if event.actor_id == target.template.id and event.event_type == "initiative")
    assert target_init.attack_roll is not None
    assert target_init.attack_roll.mode is RollMode.NORMAL
    assert target_init.feature_id is None


def test_surprise_and_invisible_cancel_on_initiative() -> None:
    state = build_combatant_state(build_goblin_warrior())
    state.conditions.add(ConditionKind.INVISIBLE)

    events, _, _ = roll_initiative_order(
        [state],
        FixedDiceProvider([12]),
        surprised_actor_ids={state.template.id},
    )

    assert events[0].attack_roll is not None
    assert events[0].attack_roll.mode is RollMode.NORMAL
    assert "Invisible grants Advantage" in events[0].description
    assert "Surprise imposes Disadvantage" in events[0].description
