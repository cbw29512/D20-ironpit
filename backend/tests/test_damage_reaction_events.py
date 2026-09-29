from __future__ import annotations

import pytest

from app.combat.damage_reaction_events import applied_damage_total, resolve_damage_event_reactions
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.character_builds import AbilityScores
from app.domain.reactions import DamageReactionAttack
from app.domain.progression_primitives import (
    SourceDamageTemporaryHpGrant,
    SourceReducesHostileToZeroHpTemporaryHp,
)


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


def test_applied_damage_total_treats_zero_loss_snapshots_as_authoritative() -> None:
    """A raw roll must not resurrect damage that defenses reduced to zero."""
    hero, monster, setup = _setup()
    event = _triggering_attack(monster, hero, setup)
    assert event.damage_roll is not None
    assert event.damage_roll.total > 0

    event = event.model_copy(update={
        "damage_components": [],
        "hp_before": 10,
        "hp_after": 10,
        "temporary_hp_before": 0,
        "temporary_hp_after": 0,
    })

    assert applied_damage_total(event) == 0


def test_source_zero_hp_trigger_grants_temporary_hp_without_class_dispatch() -> None:
    hero, monster, setup = _setup()
    hero.state.template.level = 3
    hero.state.template.ability_scores = AbilityScores(
        strength=10, dexterity=10, constitution=10,
        intelligence=10, wisdom=10, charisma=16,
    )
    hero.state.template.progression_features.source_reduces_hostile_to_zero_hp_temporary_hp = (
        SourceReducesHostileToZeroHpTemporaryHp(
            source_id="test-zero-hp-boon", source_name="Test Zero HP Boon",
            ability="charisma", per_level=1, minimum=1,
        )
    )
    monster.state.current_hp = 1
    event = _triggering_attack(hero, monster, setup)
    assert event.hp_before == 1
    assert event.hp_after == 0

    followups, sequence = resolve_damage_event_reactions(
        2, 1, hero, event, setup, FixedDiceProvider([19, 5]),
    )

    assert followups[0].event_type == "feature"
    assert followups[0].feature_id == "test-zero-hp-boon"
    assert hero.state.temporary_hp == 6
    assert sequence == 3


def test_source_zero_hp_trigger_requires_fresh_hostile_transition() -> None:
    hero, monster, setup = _setup()
    hero.state.template.level = 3
    hero.state.template.ability_scores = AbilityScores(
        strength=10, dexterity=10, constitution=10,
        intelligence=10, wisdom=10, charisma=16,
    )
    hero.state.template.progression_features.source_reduces_hostile_to_zero_hp_temporary_hp = (
        SourceReducesHostileToZeroHpTemporaryHp(
            source_id="test-zero-hp-boon", source_name="Test Zero HP Boon",
            ability="charisma", per_level=1,
        )
    )
    event = _triggering_attack(hero, monster, setup).model_copy(update={"hp_before": 0, "hp_after": 0})

    followups, sequence = resolve_damage_event_reactions(
        2, 1, hero, event, setup, FixedDiceProvider([19, 5]),
    )

    assert all(item.feature_id != "test-zero-hp-boon" for item in followups)
    assert hero.state.temporary_hp == 0
    assert sequence == 2



def test_source_damage_trigger_grants_ability_scaled_temporary_hp() -> None:
    hero, monster, setup = _setup()
    hero.state.template.ability_scores = AbilityScores(
        strength=10, dexterity=10, constitution=10,
        intelligence=10, wisdom=20, charisma=10,
    )
    hero.state.template.progression_features.source_damage_temporary_hp = SourceDamageTemporaryHpGrant(
        source_id="test-damage-vitality",
        source_name="Test Damage Vitality",
        trigger_action_ids=["sacred-flame"],
        ability="wisdom",
        ability_multiplier=2,
    )
    event = _triggering_attack(hero, monster, setup).model_copy(
        update={"feature_id": "sacred-flame"},
    )

    followups, sequence = resolve_damage_event_reactions(
        2, 1, hero, event, setup, FixedDiceProvider([19, 5]),
    )

    assert followups[0].feature_id == "test-damage-vitality"
    assert hero.state.temporary_hp == 10
    assert sequence == 3


def test_source_damage_trigger_requires_matching_action_and_actual_damage() -> None:
    hero, monster, setup = _setup()
    hero.state.template.ability_scores = AbilityScores(
        strength=10, dexterity=10, constitution=10,
        intelligence=10, wisdom=20, charisma=10,
    )
    hero.state.template.progression_features.source_damage_temporary_hp = SourceDamageTemporaryHpGrant(
        source_id="test-damage-vitality",
        source_name="Test Damage Vitality",
        trigger_action_ids=["sacred-flame"],
        ability="wisdom",
        ability_multiplier=2,
    )
    event = _triggering_attack(hero, monster, setup).model_copy(
        update={"feature_id": "guiding-bolt"},
    )
    followups, sequence = resolve_damage_event_reactions(
        2, 1, hero, event, setup, FixedDiceProvider([19, 5]),
    )
    assert all(item.feature_id != "test-damage-vitality" for item in followups)
    assert hero.state.temporary_hp == 0
    assert sequence == 2

    zero_event = event.model_copy(update={
        "feature_id": "sacred-flame",
        "damage_components": [],
        "hp_before": 10,
        "hp_after": 10,
        "temporary_hp_before": 0,
        "temporary_hp_after": 0,
    })
    followups, sequence = resolve_damage_event_reactions(
        2, 1, hero, zero_event, setup, FixedDiceProvider([19, 5]),
    )
    assert all(item.feature_id != "test-damage-vitality" for item in followups)
    assert hero.state.temporary_hp == 0
    assert sequence == 2
