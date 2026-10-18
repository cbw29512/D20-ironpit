"""Source-proof included weapon damage for reusable magical poison riders."""
from __future__ import annotations

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_included_weapon_traits_2014 import (
    included_weapon_trait_names_2014,
    weapon_damage_source_qualifiers_2014,
)
from app.domain.weapons import DamageSourceQualifier


def test_hellish_weapon_source_binding_fails_closed_for_missing_printed_clause():
    monster = next(row for row in load_monster_source_2014() if row.id == "erinyes")
    empty = monster.model_copy(update={"source_traits": ""})
    assert "Hellish Weapons" not in included_weapon_trait_names_2014(empty)


def test_hellish_weapon_binding_never_invents_damage_or_magical_tag():
    monster = next(row for row in load_monster_source_2014() if row.id == "erinyes")
    bound = included_weapon_trait_names_2014(monster)
    tags = weapon_damage_source_qualifiers_2014(monster)
    if "Hellish Weapons" in bound:
        assert DamageSourceQualifier.MAGICAL in tags
        assert monster.attacks
        assert all(attack.on_hit_damage for attack in monster.attacks)
    else:
        # Do not promote source admission without every weapon's poison rider.
        assert "Hellish Weapons" not in bound
