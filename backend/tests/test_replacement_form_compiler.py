from __future__ import annotations

from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.replacement_form_compiler import compile_replacement_form_template


def test_level_two_wolf_form_comes_from_certified_2014_roster() -> None:
    wolf = canonical_wild_shape_template_2014(2)
    assert wolf.id == "2014-wolf"
    assert wolf.challenge_rating == "1/4"
    assert wolf.ruleset == "2014"


def test_active_wolf_form_uses_beast_physical_and_druid_mental_stats() -> None:
    thalen = build_thalen_greenbough_2014(1)
    wolf = canonical_wild_shape_template_2014(2)
    active = compile_replacement_form_template(thalen, wolf)

    assert active.kind == "character"
    assert active.ability_scores is not None
    assert wolf.ability_scores is not None
    assert thalen.ability_scores is not None
    assert active.ability_scores.strength == wolf.ability_scores.strength
    assert active.ability_scores.dexterity == wolf.ability_scores.dexterity
    assert active.ability_scores.constitution == wolf.ability_scores.constitution
    assert active.ability_scores.intelligence == thalen.ability_scores.intelligence
    assert active.ability_scores.wisdom == thalen.ability_scores.wisdom
    assert active.ability_scores.charisma == thalen.ability_scores.charisma
    assert active.armor_class == wolf.armor_class
    assert active.speed_ft == wolf.speed_ft
    assert active.weapon_attack.weapon.id == wolf.weapon_attack.weapon.id
    assert active.spell_attack_actions == []
    assert active.spell_save_actions == []
    assert active.defensive_spell_actions == []
