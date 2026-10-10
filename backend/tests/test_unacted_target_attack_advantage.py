"""The same opening-turn Advantage primitive is available to every combatant source."""

from types import SimpleNamespace

from app.combat.attack_roll_resolution import first_turn_target_advantage_sources
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import progression_features_2014, bound_trait_names_2014


def test_unacted_target_advantage_is_source_driven_and_expires_after_first_turn():
    attacker = SimpleNamespace(template=SimpleNamespace(
        progression_features=SimpleNamespace(advantage_against_unacted_targets=True),
    ))
    defender = SimpleNamespace(turns_started=0)
    assert first_turn_target_advantage_sources(attacker, defender) == 1
    defender.turns_started = 1
    assert first_turn_target_advantage_sources(attacker, defender) == 0
    attacker.template.progression_features.advantage_against_unacted_targets = False
    defender.turns_started = 0
    assert first_turn_target_advantage_sources(attacker, defender) == 0


def test_2014_assassin_binds_generic_unacted_target_flag():
    roster = load_monster_source_2014()
    assassin = next(item for item in roster if item.id == "assassin")
    assert "Assassinate" in assassin.trait_names
    assert progression_features_2014(assassin).advantage_against_unacted_targets
    assert progression_features_2014(assassin).critical_hits_against_surprised_targets
    assert "Assassinate" in bound_trait_names_2014(assassin)
    other = next(item for item in roster if item.id == "goblin")
    assert not progression_features_2014(other).advantage_against_unacted_targets
    assert not progression_features_2014(other).critical_hits_against_surprised_targets
