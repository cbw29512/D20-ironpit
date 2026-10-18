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


def test_source_neutral_included_poison_damage_positive_and_mutation():
    source = next(row for row in load_monster_source_2014() if row.id == "erinyes")
    attack = source.attacks[0].model_copy(update={
        "id": "poison-blade", "name": "Poison Blade", "kind": "melee",
        "on_hit_damage": [{"dice_count": 3, "dice_size": 8, "bonus": 0, "type": "poison"}],
    })
    damage = attack.damage
    synthetic = source.model_copy(update={
        "name": "Synthetic fiend",
        "trait_names": ["Hellish Weapons"],
        "attacks": [attack],
        "source_traits": (
            "<p><strong>Hellish Weapons.</strong> The fiend's weapon attacks are magical "
            "and deal an extra 13 (3d8) poison damage on a hit (included in the attacks).</p>"
        ),
        "source_actions": (
            "<p><strong>Poison Blade.</strong> Melee Weapon Attack: +8 to hit. "
            f"Hit: {damage.average} ({damage.dice_count}d{damage.dice_size} + {damage.bonus}) "
            f"{damage.type} damage plus 13 (3d8) poison damage.</p>"
        ),
    })
    assert included_weapon_trait_names_2014(synthetic) == frozenset({"Hellish Weapons"})
    assert DamageSourceQualifier.MAGICAL in weapon_damage_source_qualifiers_2014(synthetic)
    missing_rider = synthetic.model_copy(update={
        "attacks": [attack.model_copy(update={"on_hit_damage": []})],
    })
    assert "Hellish Weapons" not in included_weapon_trait_names_2014(missing_rider)
