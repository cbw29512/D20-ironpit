"""Assassin Evasion reuses the same passive Dexterity-save damage behavior as Rogue."""
from types import SimpleNamespace

from app.combat.rogue_defenses import evasion_damage
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import progression_features_2014, bound_trait_names_2014


def test_2014_assassin_evasion_binds_shared_passive():
    assassin = next(m for m in load_monster_source_2014() if m.id == "assassin")
    grants = progression_features_2014(assassin)
    assert grants.evasion
    assert grants.evasion_disabled_while_incapacitated
    assert "Evasion" in bound_trait_names_2014(assassin)


def test_shared_evasion_passive_damage_cases(monkeypatch):
    # The same universal modifier applies regardless of the printed source identity.
    features = SimpleNamespace(evasion=True, evasion_disabled_while_incapacitated=True)
    state = SimpleNamespace(template=SimpleNamespace(progression_features=features))
    monkeypatch.setattr("app.combat.rogue_defenses.is_incapacitated", lambda _: False)
    assert evasion_damage(state, "dexterity", True, "half", 30) == 0
    assert evasion_damage(state, "dexterity", False, "half", 30) == 15
    assert evasion_damage(state, "constitution", True, "half", 30) == 15
    assert evasion_damage(state, "dexterity", True, "none", 30) == 30
    # A combatant without the passive buff uses the ordinary save/damage rule.
    # This is the same save event, not a special alternate Evasion resolver.
    features.evasion = False
    assert evasion_damage(state, "dexterity", True, "half", 30) == 15
    assert evasion_damage(state, "dexterity", False, "half", 30) == 30
    features.evasion = True
    monkeypatch.setattr("app.combat.rogue_defenses.is_incapacitated", lambda _: True)
    assert evasion_damage(state, "dexterity", True, "half", 30) == 15
    assert evasion_damage(state, "dexterity", False, "half", 30) == 30
