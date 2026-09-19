from app.combat.damage_reaction_dispatch import applied_damage_total, resolve_damage_event_reactions
from app.combat.damage_triggered_reactions import resolve_damage_triggered_melee_reaction
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.reactions import DamageTriggeredMeleeReaction


def _member(combatant_id, side, position, template):
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(distance: int = 5):
    reactor_template = build_demo_fighter()
    reactor_template.damage_triggered_melee_reaction = DamageTriggeredMeleeReaction(
        id="retaliation",
        trigger_range_ft=5,
    )
    reactor = _member("hero-1", "heroes", 0, reactor_template)
    source = _member("monster-1", "monsters", distance, build_goblin_warrior())
    setup = EncounterSetup(
        heroes=[reactor],
        monsters=[source],
        hero_total_levels=1,
        monster_total_cr="1/4",
    )
    return reactor, source, setup


def test_damage_triggered_melee_reaction_spends_only_reaction_and_attacks_source() -> None:
    reactor, source, setup = _setup()
    hp_before = source.state.current_hp

    event = resolve_damage_triggered_melee_reaction(
        4,
        2,
        reactor,
        source,
        setup,
        FixedDiceProvider([19, 5]),
        turn_key="2:monster-1",
    )

    assert event is not None
    assert event.event_type == "attack"
    assert event.feature_id == "retaliation"
    assert event.actor_id == reactor.combatant_id
    assert event.target_id == source.combatant_id
    assert source.state.current_hp < hp_before
    assert reactor.state.reaction_available is False
    assert reactor.state.action_available is True
    assert event.turn_terminated is False


def test_damage_triggered_melee_reaction_requires_source_within_trigger_range() -> None:
    reactor, source, setup = _setup(distance=10)

    event = resolve_damage_triggered_melee_reaction(
        1, 1, reactor, source, setup, FixedDiceProvider([19, 5]),
    )

    assert event is None
    assert reactor.state.reaction_available is True


def test_damage_triggered_melee_reaction_requires_available_reaction() -> None:
    reactor, source, setup = _setup()
    reactor.state.reaction_available = False

    event = resolve_damage_triggered_melee_reaction(
        1, 1, reactor, source, setup, FixedDiceProvider([19, 5]),
    )

    assert event is None


def test_damage_triggered_melee_reaction_requires_declared_melee_weapon() -> None:
    reactor, source, setup = _setup()
    ranged = source.state.template.alternate_weapon_attacks[0]
    reactor.state.template.weapon_attack = ranged
    reactor.state.template.alternate_weapon_attacks = []

    event = resolve_damage_triggered_melee_reaction(
        1, 1, reactor, source, setup, FixedDiceProvider([19, 5]),
    )

    assert event is None
    assert reactor.state.reaction_available is True


def test_damage_event_dispatch_triggers_immediate_reaction_after_applied_damage() -> None:
    reactor, source, setup = _setup()
    triggering = resolve_encounter_attack(
        1,
        1,
        source,
        reactor,
        source.state.template.weapon_attack,
        5,
        FixedDiceProvider([19, 4]),
        setup,
        spend_action=False,
    )

    reactions, sequence = resolve_damage_event_reactions(
        2,
        1,
        source,
        triggering,
        setup,
        FixedDiceProvider([19, 5]),
        turn_key="1:monster-1",
    )

    assert len(reactions) == 1
    assert reactions[0].feature_id == "retaliation"
    assert reactions[0].actor_id == reactor.combatant_id
    assert reactions[0].target_id == source.combatant_id
    assert sequence == 3


def test_damage_event_dispatch_ignores_event_without_applied_damage() -> None:
    reactor, source, setup = _setup()
    source.state.template.armor_class = 99
    triggering = resolve_encounter_attack(
        1,
        1,
        reactor,
        source,
        reactor.state.template.weapon_attack,
        5,
        FixedDiceProvider([2]),
        setup,
        spend_action=False,
        off_turn=True,
    )

    reactions, sequence = resolve_damage_event_reactions(
        2,
        1,
        reactor,
        triggering,
        setup,
        FixedDiceProvider([19, 5]),
    )

    assert triggering.damage_roll is None
    assert reactions == []
    assert sequence == 2


def test_damage_event_dispatch_allows_one_counter_reaction_per_creature() -> None:
    reactor, source, setup = _setup()
    source.state.template.damage_triggered_melee_reaction = DamageTriggeredMeleeReaction(
        id="counter-retaliation",
        trigger_range_ft=5,
    )
    triggering = resolve_encounter_attack(
        1,
        1,
        source,
        reactor,
        source.state.template.weapon_attack,
        5,
        FixedDiceProvider([19, 4]),
        setup,
        spend_action=False,
    )

    reactions, sequence = resolve_damage_event_reactions(
        2,
        1,
        source,
        triggering,
        setup,
        FixedDiceProvider([19, 5, 19, 4]),
        turn_key="1:monster-1",
    )

    assert [event.feature_id for event in reactions] == [
        "retaliation",
        "counter-retaliation",
    ]
    assert sequence == 4
    assert reactor.state.reaction_available is False
    assert source.state.reaction_available is False



def test_applied_damage_total_prefers_defended_component_amounts() -> None:
    reactor, source, setup = _setup()
    event = resolve_encounter_attack(
        1, 1, source, reactor, source.state.template.weapon_attack, 5,
        FixedDiceProvider([19, 4]), setup, spend_action=False,
    )
    assert event.damage_roll is not None
    assert event.damage_roll.total > 0
    event = event.model_copy(update={
        "damage_components": [
            part.model_copy(update={"applied_total": 0})
            for part in event.damage_components
        ],
    })
    assert applied_damage_total(event) == 0


def test_damage_triggered_reaction_is_blocked_while_reactor_is_unconscious() -> None:
    reactor, source, setup = _setup()
    reactor.state.is_unconscious = True

    event = resolve_damage_triggered_melee_reaction(
        1, 1, reactor, source, setup, FixedDiceProvider([19, 5]),
    )

    assert event is None
    assert reactor.state.reaction_available is True
