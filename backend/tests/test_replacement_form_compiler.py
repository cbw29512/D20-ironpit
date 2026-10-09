from __future__ import annotations

import pytest
import json
from fractions import Fraction
from pathlib import Path

from app.domain.character_builds import AbilityScores
from app.domain.weapons import DamageType

from app.content.druid_2014_wild_shape_forms import canonical_wild_shape_template_2014
from app.content.druid_land_2014_runtime import build_thalen_greenbough_2014
from app.content.replacement_form_compiler import (
    compile_replacement_form_template,
    compile_monster_change_shape_physical_overlay,
)


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


def test_monster_change_shape_overlay_retains_owner_con_hp_and_defenses() -> None:
    wolf = canonical_wild_shape_template_2014(2)
    assert wolf.kind == "monster"
    deva = wolf.model_copy(update={
        "id": "2014-deva-overlay-test", "name": "Deva",
        "kind": "monster", "creature_type": "celestial", "challenge_rating": "10",
        "max_hp": 136, "armor_class": 17,
        "ability_scores": AbilityScores(
            strength=18, dexterity=18, constitution=18,
            intelligence=17, wisdom=20, charisma=20,
        ),
        "saving_throw_bonuses": {"wisdom": 9, "charisma": 9},
        "damage_resistances": [DamageType.RADIANT],
        "condition_immunities": ["charmed"],
    }, deep=True)

    # Synthetic source-defenses, explicitly attached to this legal beast
    # fixture, prove additive overlay without inventing defenses for real Wolf.
    defended_wolf = wolf.model_copy(update={
        "damage_resistances": [DamageType.FIRE],
        "damage_immunities": [DamageType.POISON],
        "condition_immunities": ["poisoned"],
    }, deep=True)
    active = compile_monster_change_shape_physical_overlay(deva, defended_wolf)
    assert active.id == f"{deva.id}--form-{wolf.id}"
    assert active.kind == "monster"
    assert active.creature_type == "celestial"
    assert active.max_hp == 136
    assert active.armor_class == wolf.armor_class
    assert active.movement_modes == wolf.movement_modes
    assert active.ability_scores == AbilityScores(
        strength=wolf.ability_scores.strength,
        dexterity=wolf.ability_scores.dexterity,
        constitution=18, intelligence=17, wisdom=20, charisma=20,
    )
    assert active.saving_throw_bonuses == deva.saving_throw_bonuses
    assert active.damage_resistances == [DamageType.RADIANT, DamageType.FIRE]
    assert active.damage_immunities == [DamageType.POISON]
    assert active.condition_immunities == ["charmed", "poisoned"]
    assert deva.damage_resistances == [DamageType.RADIANT]
    assert wolf.damage_resistances == []
    assert active.weapon_attack == deva.weapon_attack
    assert deva.ability_scores.strength == 18
    assert deva.armor_class == 17


def test_monster_change_shape_overlay_rejects_illegal_sources() -> None:
    wolf = canonical_wild_shape_template_2014(2)
    deva = wolf.model_copy(update={
        "id": "2014-deva-overlay-test", "kind": "monster",
        "creature_type": "celestial", "challenge_rating": "10",
    }, deep=True)
    with pytest.raises(ValueError, match="ruleset"):
        compile_monster_change_shape_physical_overlay(
            deva, wolf.model_copy(update={"ruleset": "2024"})
        )
    with pytest.raises(ValueError, match="humanoid or beast"):
        compile_monster_change_shape_physical_overlay(
            deva, wolf.model_copy(update={"creature_type": "celestial"})
        )
    with pytest.raises(ValueError, match="challenge rating"):
        compile_monster_change_shape_physical_overlay(
            deva, wolf.model_copy(update={"challenge_rating": "11"})
        )
    with pytest.raises(ValueError, match="two monster"):
        compile_monster_change_shape_physical_overlay(
            deva.model_copy(update={"kind": "character"}), wolf
        )


def test_deva_shortlist_is_bounded_to_certified_2014_beasts() -> None:
    from app.content.ruleset_monster_rosters import build_monster_templates_for_ruleset

    root = Path(__file__).resolve().parents[2]
    spec = json.loads((root / "data/monster_2014_change_shape_shortlists.json").read_text())
    assert spec["schema_version"] == 1 and spec["ruleset"] == "2014"
    assert len(spec["policies"]) == 1
    policy = spec["policies"][0]
    assert policy["source_monster"] == "Deva"
    assert policy["keep_original_form_when_not_beneficial"] is True
    ids = policy["form_template_ids"]
    assert len(ids) == len(set(ids)) == len(policy["candidate_profiles"]) == 4
    assert len(ids) <= policy["max_selected_forms"]
    assert {row["form_template_id"] for row in policy["candidate_profiles"]} == set(ids)

    ready = {monster.id: monster for monster in build_monster_templates_for_ruleset("2014")}
    for ident in ids:
        assert ident in ready, f"{ident} is not a certified 2014 form"
        form = ready[ident]
        assert form.kind == "monster" and form.ruleset == "2014"
        assert (form.creature_type or "").casefold() in {"beast", "humanoid"}
        assert form.challenge_rating is not None
        assert Fraction(form.challenge_rating) <= Fraction(policy["source_cr"])
    fire_form = ready["2014-half-red-dragon-veteran"]
    assert fire_form.armor_class == 18
    assert DamageType.FIRE in fire_form.damage_resistances
    assert not any("werebear" in ident for ident in ids), "Uncertified Werebear is not available"
