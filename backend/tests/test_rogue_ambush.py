from app.combat.engine import run_duel
from app.content.demo import build_goblin_warrior
from app.content.rogue import build_demo_rogue
from app.domain.models import (
    ActorVisibilityState,
    EncounterSetup,
    PrecombatActorPlan,
    RollMode,
)


class SteadyAmbushDice:
    def roll(self, sides: int) -> int:
        if sides == 20:
            return 15
        if sides == 6:
            return 4
        if sides == 10:
            return 6
        return max(1, sides // 2)


def test_level_one_rogue_can_open_from_precombat_stealth_with_sneak_attack() -> None:
    rogue = build_demo_rogue()
    goblin = build_goblin_warrior()
    visibility = {
        rogue.id: ActorVisibilityState(
            heavily_obscured=True,
            enemy_line_of_sight=False,
        )
    }
    setup = EncounterSetup(
        plans_by_actor={
            rogue.id: PrecombatActorPlan(
                attempt_hide=True,
                ambush_target_ids={goblin.id},
            )
        }
    )

    battle = run_duel(
        rogue,
        goblin,
        SteadyAmbushDice(),
        starting_distance_ft=60,
        visibility_by_actor=visibility,
        encounter_setup=setup,
    )

    assert [event.event_type for event in battle.events[:3]] == [
        "hide", "initiative", "initiative"
    ]
    rogue_init = next(
        event for event in battle.events
        if event.event_type == "initiative" and event.actor_id == rogue.id
    )
    goblin_init = next(
        event for event in battle.events
        if event.event_type == "initiative" and event.actor_id == goblin.id
    )
    opening_attack = next(
        event for event in battle.events
        if event.event_type == "attack" and event.actor_id == rogue.id
    )

    assert rogue_init.attack_roll is not None
    assert rogue_init.attack_roll.mode is RollMode.ADVANTAGE
    assert goblin_init.attack_roll is not None
    assert goblin_init.attack_roll.mode is RollMode.DISADVANTAGE
    assert opening_attack.weapon_id == "shortbow"
    assert opening_attack.attack_roll is not None
    assert opening_attack.attack_roll.mode is RollMode.ADVANTAGE
    assert any(
        component.source == "Sneak Attack"
        for component in opening_attack.damage_components
    )
    assert opening_attack.damage_roll is not None
    assert opening_attack.damage_roll.total == 11
    assert battle.winner_id == rogue.id
    assert battle.fighter.hidden is False
