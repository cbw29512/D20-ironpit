from __future__ import annotations

import pytest

from app.combat.damage_reaction_events import applied_damage_total, resolve_damage_event_reactions
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
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


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    hero_template = build_demo_fighter()
    hero_template.damage_reaction_attack = DamageReactionAttack(source_feature="retaliation")
    hero = _member("hero-1", "heroes", 0, hero_template)
    monster = _member("monster-1", "monsters", 5, build_goblin_warrior())
    setup = EncounterSetup(
        heroes=[hero],
        monsters=[monster],
        hero_total_levels=1,
        monster_total_cr="1/4",
    )
    return hero, monster, setup


def _triggering_attack(
    source: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
):
    return resolve_encounter_attack(
        1,
        1,
        source,
        target,
        source.state.template.weapon_attack,
        5,
        FixedDiceProvider([19, 4]),
        setup,
        spend_action=False,
    )


def test_damage_event_dispatch_runs_immediately_after_applied_damage() -> None:
    hero, monster, setup = _setup()
    triggering = _triggering_attack(monster, hero, setup)

    reactions, sequence = resolve_damage_event_reactions(
        2,
        1,
        monster,
        triggering,
        setup,
        FixedDiceProvider([19, 5]),
        turn_key="1:monster-1",
    )

    assert len(reactions) == 1
    assert reactions[0].feature_id == "retaliation"
    assert reactions[0].actor_id == hero.combatant_id
    assert reactions[0].target_id == monster.combatant_id
    assert sequence == 3


def test_damage_event_dispatch_ignores_zero_applied_damage() -> None:
    hero, monster, setup = _setup()
    hero.state.template.armor_class = 99
    triggering = _triggering_attack(monster, hero, setup)

    reactions, sequence = resolve_damage_event_reactions(
        2,
        1,
        monster,
        triggering,
        setup,
        FixedDiceProvider([19, 5]),
    )

    assert applied_damage_total(triggering) == 0
    assert reactions == []
    assert sequence == 2


def test_damage_event_dispatch_rejects_mismatched_source_provenance() -> None:
    hero, monster, setup = _setup()
    triggering = _triggering_attack(monster, hero, setup)

    with pytest.raises(ValueError, match="source must match"):
        resolve_damage_event_reactions(
            2,
            1,
            hero,
            triggering,
            setup,
            FixedDiceProvider([19, 5]),
        )


def test_damage_event_dispatch_allows_one_counter_reaction_per_creature() -> None:
    hero, monster, setup = _setup()
    monster.state.template.damage_reaction_attack = DamageReactionAttack(
        source_feature="counter-retaliation",
    )
    triggering = _triggering_attack(monster, hero, setup)

    reactions, sequence = resolve_damage_event_reactions(
        2,
        1,
        monster,
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
    assert hero.state.reaction_available is False
    assert monster.state.reaction_available is False


def test_applied_damage_total_prefers_applied_components() -> None:
    hero, monster, setup = _setup()
    event = _triggering_attack(monster, hero, setup)
    event = event.model_copy(update={
        "damage_components": [
            component.model_copy(update={"applied_total": 0})
            for component in event.damage_components
        ],
    })

    assert event.damage_roll is not None
    assert event.damage_roll.total > 0
    assert applied_damage_total(event) == 0
