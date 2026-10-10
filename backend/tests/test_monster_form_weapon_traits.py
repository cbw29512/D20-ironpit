from __future__ import annotations

import pytest
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_angelic_weapon_rider_2014 import source_angelic_weapon_hit_rider_2014
from app.combat.monster_form_weapon_traits import inherit_weapon_hit_trait_for_form
from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.domain.weapons import DamageType, OnHitDamage
from app.domain.damage_sources import DamageSourceQualifier


def _sources():
    wolf = canonical_wild_shape_template_2014(2)
    mace = wolf.weapon_attack.model_copy(update={
        "id": "source-mace",
        "on_hit_damage": [OnHitDamage(
            source="printed-owner-mace", dice_count=4, dice_size=8,
            damage_type=DamageType.RADIANT)],
        "damage_source_qualifiers": [DamageSourceQualifier.MAGICAL],
    }, deep=True)
    owner = wolf.model_copy(update={
        "id": "source-owner", "kind": "monster", "weapon_attack": mace,
        "alternate_weapon_attacks": [],
    }, deep=True)
    form = wolf.model_copy(update={
        "id": "printed-form", "kind": "monster",
    }, deep=True)
    return owner, form


def test_source_radiant_dice_are_validated_per_angel_not_hardcoded():
    source = {row.id: row for row in load_monster_source_2014()}
    for id_, count in (("deva", 4), ("planetar", 5), ("solar", 6)):
        rider = source_angelic_weapon_hit_rider_2014(source[id_])
        assert rider.dice_count == count
        assert rider.dice_size == 8 and rider.damage_type == DamageType.RADIANT
        assert id_ in rider.source
    with pytest.raises(ValueError, match="not independently validated"):
        source_angelic_weapon_hit_rider_2014(source["giant-scorpion"])


def test_retained_owner_4d8_is_not_doubled_and_form_weapon_gains_one_rider():
    owner, form = _sources()
    rider = source_angelic_weapon_hit_rider_2014(
        next(item for item in load_monster_source_2014() if item.id == "deva")
    )
    profiles = (owner.weapon_attack, form.weapon_attack)
    result = inherit_weapon_hit_trait_for_form(
        owner, form, profiles, inherited_rider=rider, magical_weapons=True
    )
    assert len(result) == 2
    assert result[0].on_hit_damage == owner.weapon_attack.on_hit_damage
    assert len(result[0].on_hit_damage) == 1
    assert result[1].on_hit_damage == [rider]
    assert result[1].damage_source_qualifiers == [DamageSourceQualifier.MAGICAL]
    assert form.weapon_attack.on_hit_damage == []
    repeated = inherit_weapon_hit_trait_for_form(
        owner, form, result, inherited_rider=rider, magical_weapons=True
    )
    assert repeated == result
    assert len(repeated[1].on_hit_damage) == 1


def test_source_collision_and_spoofed_inventory_fail_closed():
    owner, form = _sources()
    rider = OnHitDamage(source="explicit-source", dice_count=4, dice_size=8,
                      damage_type=DamageType.RADIANT)
    with pytest.raises(ValueError, match="inventory"):
        inherit_weapon_hit_trait_for_form(owner, form, (owner.weapon_attack,),
            inherited_rider=rider, magical_weapons=True)
    with pytest.raises(ValueError, match="not collide"):
        same_id = form.weapon_attack.model_copy(update={"id": "source-mace"})
        inherit_weapon_hit_trait_for_form(owner, form.model_copy(update={"weapon_attack": same_id}),
            (owner.weapon_attack, same_id), inherited_rider=rider, magical_weapons=True)
    conflicting = form.weapon_attack.model_copy(update={"on_hit_damage": [
        OnHitDamage(source="explicit-source", dice_count=5, dice_size=8, damage_type=DamageType.RADIANT)
    ]})
    with pytest.raises(ValueError, match="conflicts"):
        inherit_weapon_hit_trait_for_form(owner, form,
            (owner.weapon_attack, conflicting), inherited_rider=rider, magical_weapons=True)
