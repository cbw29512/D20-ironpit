from app.combat.damage_reactions import event_applied_damage, resolve_post_damage_reactions
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DiceRoll
from app.domain.progression import DamageTriggeredReactionAttack


def _member(combatant_id: str, side: str, position: int, *, retaliation: bool) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(deep=True)
    progression = template.progression_features.model_copy(update={
        "damage_triggered_reaction_attack": (
            DamageTriggeredReactionAttack(source_id="test-retaliation") if retaliation else None
        ),
    })
    template = template.model_copy(update={
        "armor_class": 10,
        "max_hp": 50,
        "progression_features": progression,
    })
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _damage_event(source: EncounterCombatant, target: EncounterCombatant, total: int = 4) -> BattleEvent:
    return BattleEvent(
        sequence=1,
        round_number=1,
        event_type="attack",
        actor_id=source.combatant_id,
        actor_name=source.state.template.name,
        target_id=target.combatant_id,
        target_name=target.state.template.name,
        damage_roll=DiceRoll(notation=str(total), rolls=[], modifier=0, total=total),
        hp_before=50,
        hp_after=50 - total,
        animation="slash",
        description="Synthetic damage trigger.",
    )


def test_damage_event_requires_positive_applied_damage() -> None:
    source = _member("source", "monsters", 5, retaliation=False)
    target = _member("target", "heroes", 0, retaliation=True)
    assert event_applied_damage(_damage_event(source, target, 4)) is True
    assert event_applied_damage(_damage_event(source, target, 0)) is False


def test_nearby_damage_spends_reaction_and_resolves_melee_attack() -> None:
    source = _member("source", "monsters", 5, retaliation=False)
    reactor = _member("reactor", "heroes", 0, retaliation=True)
    setup = EncounterSetup(heroes=[reactor], monsters=[source], hero_total_levels=1, monster_total_cr="1")

    events, sequence = resolve_post_damage_reactions(
        2, 1, source, _damage_event(source, reactor), setup,
        FixedDiceProvider([15, 4]), turn_key="1:source",
    )

    assert sequence == 3
    assert len(events) == 1
    assert events[0].actor_id == reactor.combatant_id
    assert events[0].target_id == source.combatant_id
    assert events[0].feature_id == "test-retaliation"
    assert reactor.state.reaction_available is False
    assert source.state.current_hp < source.state.template.max_hp


def test_reaction_does_not_fire_out_of_range_or_without_reaction() -> None:
    source = _member("source", "monsters", 10, retaliation=False)
    reactor = _member("reactor", "heroes", 0, retaliation=True)
    setup = EncounterSetup(heroes=[reactor], monsters=[source], hero_total_levels=1, monster_total_cr="1")

    events, sequence = resolve_post_damage_reactions(
        2, 1, source, _damage_event(source, reactor), setup,
        FixedDiceProvider([15, 4]),
    )
    assert (events, sequence) == ([], 2)

    source.position_ft = 5
    reactor.state.reaction_available = False
    events, sequence = resolve_post_damage_reactions(
        2, 1, source, _damage_event(source, reactor), setup,
        FixedDiceProvider([15, 4]),
    )
    assert (events, sequence) == ([], 2)


def test_two_sided_damage_reactions_terminate_after_each_reaction_is_spent() -> None:
    source = _member("source", "monsters", 5, retaliation=True)
    reactor = _member("reactor", "heroes", 0, retaliation=True)
    setup = EncounterSetup(heroes=[reactor], monsters=[source], hero_total_levels=1, monster_total_cr="1")

    events, sequence = resolve_post_damage_reactions(
        2, 1, source, _damage_event(source, reactor), setup,
        FixedDiceProvider([15, 4, 15, 4]), turn_key="1:source",
    )

    assert sequence == 4
    assert [event.actor_id for event in events] == ["reactor", "source"]
    assert all(event.feature_id == "test-retaliation" for event in events)
    assert reactor.state.reaction_available is False
    assert source.state.reaction_available is False
