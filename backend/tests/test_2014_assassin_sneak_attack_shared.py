"""2014 Assassin uses the same Sneak Attack primitive as Rogue and Spy."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import (
    bound_trait_names_2014, progression_features_2014, sneak_attack_eligible_2014,
)


def test_assassin_sneak_attack_uses_shared_rogue_damage_profile():
    assassin = next(m for m in load_monster_source_2014() if m.id == "assassin")
    assert "Sneak Attack" in assassin.trait_names
    assert progression_features_2014(assassin).sneak_attack_d6 > 0
    assert "Sneak Attack" in bound_trait_names_2014(assassin)
    assert any(sneak_attack_eligible_2014(assassin, attack) for attack in assassin.attacks)


def test_spy_existing_sneak_attack_remains_bound():
    spy = next(m for m in load_monster_source_2014() if m.id == "spy")
    assert progression_features_2014(spy).sneak_attack_d6 == 2
    assert "Sneak Attack (1/Turn)" in bound_trait_names_2014(spy)


def test_pit_sneak_attack_assumes_finesse_for_source_melee_attacks():
    """The source weapon's printed name cannot disable Sneak Attack eligibility."""
    from types import SimpleNamespace
    from app.content.monster_trait_bindings_2014 import _base_sneak_attack_eligible

    assert _base_sneak_attack_eligible(SimpleNamespace(kind="melee", name="Unlisted Melee Weapon"))
    assert _base_sneak_attack_eligible(SimpleNamespace(kind="ranged", name="Unlisted Ranged Weapon"))
    assert not _base_sneak_attack_eligible(SimpleNamespace(kind="spell", name="Spell Attack"))
