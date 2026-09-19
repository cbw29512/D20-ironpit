from __future__ import annotations

from app.combat.damage_reaction_dispatch import (
    plan_damage_reaction_attack,
    resolve_damage_reaction_attack,
)
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.reactions import DamageReactionAttack


def _member(combatant_id: str, side: str, position: int, template) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(distance: int = 5) -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    reactor_template = build_demo_fighter()
    reactor_template.damage_reaction_attack = DamageReactionAttack(source_feature="retaliation")
    reactor = _member("hero-1", "heroes", 0, reactor_template)
    source = _member("monster-source", "monsters", distance, build_goblin_warrior())
    decoy = _member("monster-decoy", "monsters", 5, build_goblin_warrior())
    setup = EncounterSetup(
        heroes=[reactor],
        monsters=[decoy, source],
        hero_total_levels=1,
        monster_total_cr="1/2",
    )
    return reactor, source, setup


def test_damage_reaction_plan_is_bound_to_triggering_source_not_normal_target_order() -> None:
    reactor, source, setup = _setup()
    plan = plan_damage_reaction_attack(reactor, source, setup, applied_damage=7)

    assert plan is not None
    assert plan.source.combatant_id == "monster-source"
    assert plan.distance_ft == 5
    assert plan.attack.weapon.attack_kind.value == "melee"


def test_damage_reaction_plan_fails_closed_out_of_range_or_without_applied_damage() -> None:
    reactor, source, setup = _setup(distance=10)

    assert plan_damage_reaction_attack(reactor, source, setup, applied_damage=7) is None

    source.position_ft = 5
    assert plan_damage_reaction_attack(reactor, source, setup, applied_damage=0) is None


def test_damage_reaction_plan_requires_available_capable_reactor() -> None:
    reactor, source, setup = _setup()

    reactor.state.reaction_available = False
    assert plan_damage_reaction_attack(reactor, source, setup, applied_damage=7) is None

    reactor.state.reaction_available = True
    reactor.state.is_unconscious = True
    assert plan_damage_reaction_attack(reactor, source, setup, applied_damage=7) is None


def test_damage_reaction_resolution_spends_only_reaction_and_attacks_source() -> None:
    reactor, source, setup = _setup()
    hp_before = source.state.current_hp
    action_before = reactor.state.action_available

    event = resolve_damage_reaction_attack(
        4,
        2,
        reactor,
        source,
        setup,
        7,
        FixedDiceProvider([19, 5]),
        turn_key="2:monster-source",
    )

    assert event is not None
    assert event.event_type == "attack"
    assert event.feature_id == "retaliation"
    assert event.actor_id == reactor.combatant_id
    assert event.target_id == source.combatant_id
    assert source.state.current_hp < hp_before
    assert reactor.state.reaction_available is False
    assert reactor.state.action_available is action_before
    assert event.turn_terminated is False
