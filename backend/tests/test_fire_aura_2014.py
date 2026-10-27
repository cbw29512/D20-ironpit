"""Source-neutral 2014 Fire Aura binding."""
from app.content.monster_fire_aura_2014 import fire_aura_2014
from app.content.monster_source_2014 import load_monster_source_2014


def _source(monster_id):
    return next(card for card in load_monster_source_2014() if card.id == monster_id)


def test_balor_fire_aura_binds_exact_parameters():
    source = _source("balor")
    action, = fire_aura_2014(source)
    assert action.id == "fire-aura" and action.name == "Fire Aura"
    assert action.activation_timing == "passive"
    emanation = action.start_turn_emanation_damage
    assert emanation is not None and emanation.radius_ft == 5
    assert (emanation.dice_count, emanation.dice_size, emanation.damage_type.value) == (3, 6, "fire")
    retaliation = action.melee_hit_retaliation
    assert retaliation is not None and retaliation.range_ft == 5 and retaliation.on_contact
    assert (retaliation.dice_count, retaliation.dice_size, retaliation.damage_type.value) == (3, 6, "fire")


def test_changed_fire_aura_clause_fails_closed():
    source = _source("balor")
    mutant = source.model_copy(update={
        "source_traits": source.source_traits.replace(
            "takes 10 (3d6) fire damage",
            "takes 5 (1d10) fire damage",
        ),
    })
    assert fire_aura_2014(mutant) == []
