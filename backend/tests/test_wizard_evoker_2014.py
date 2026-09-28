from app.combat.dice import FixedDiceProvider
from app.combat.spell_feature_rules import (
    apply_damage_maximizer_cost,
    available_cast_grant,
    legal_save_spell_levels,
    spend_cast_grant,
)
from app.combat.state import build_combatant_state
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.wizard_2014_spell_package import build_wizard_2014_spell_package
from app.content.wizard_evoker_2014_profile import build_elian_starweaver_2014_profile
from app.content.wizard_evoker_2014_runtime import build_elian_starweaver_2014
from app.domain.encounters import EncounterCombatant


def _member(level: int) -> EncounterCombatant:
    template = build_elian_starweaver_2014(level)
    return EncounterCombatant(
        combatant_id="elian", side="heroes", position_ft=0,
        state=build_combatant_state(template),
    )


def test_elian_is_legal_persistent_2014_evoker_progression() -> None:
    for level in range(1, 21):
        profile = build_elian_starweaver_2014_profile(level)
        assert_canonical_profile_policy(profile)
        assert profile.character_name == "Elian Starweaver"
        assert profile.ruleset == "2014"
        assert profile.level == level
        if level >= 2:
            assert profile.subclass_id == "evoker"


def test_elian_damage_build_reaches_intelligence_twenty() -> None:
    level_one = build_elian_starweaver_2014_profile(1)
    level_eight = build_elian_starweaver_2014_profile(8)

    assert sorted(level_one.base_ability_scores.model_dump().values()) == [8, 10, 12, 13, 14, 15]
    assert level_one.final_ability_scores.intelligence == 16
    assert level_eight.final_ability_scores.intelligence == 20


def test_sculpt_potent_and_empowered_evocation_are_universal_bindings() -> None:
    level_ten = build_elian_starweaver_2014(10)
    features = level_ten.progression_features

    sculpt = features.area_spell_ally_protection
    assert sculpt is not None and sculpt.source_id == "sculpt-spells"
    assert "fireball" in sculpt.eligible_spell_ids
    assert "lightning-bolt" in sculpt.eligible_spell_ids

    poison = next(item for item in level_ten.spell_save_actions if item.id == "poison-spray")
    fireball = next(item for item in level_ten.spell_save_actions if item.id == "fireball")
    assert poison.success_damage == "half"
    assert fireball.damage_bonus == level_ten.ability_scores.modifier("intelligence")


def test_overchannel_uses_generic_maximizer_and_repeat_self_damage() -> None:
    elian = _member(14)
    fireball = next(item for item in elian.state.template.spell_save_actions if item.id == "fireball")
    grant = elian.state.template.progression_features.spell_damage_maximizer

    assert grant is not None and grant.source_id == "overchannel"

    first, sequence = apply_damage_maximizer_cost(
        1, 1, elian, fireball, FixedDiceProvider([]), [elian.state],
    )
    assert first is None and sequence == 1
    hp_before = elian.state.current_hp

    second, sequence = apply_damage_maximizer_cost(
        1, 2, elian, fireball, FixedDiceProvider([1, 1, 1, 1, 1, 1]), [elian.state],
    )
    assert second is not None and sequence == 2
    assert second.feature_id == "overchannel"
    assert second.damage_roll is not None and second.damage_roll.notation == "6d12"
    assert second.damage_roll.total == 6
    assert elian.state.current_hp == hp_before - 6


def test_spell_mastery_grants_only_selected_base_level_free_casts() -> None:
    elian = _member(18)
    for resource in elian.state.resources:
        if resource.id in {"spell-slot-1", "spell-slot-2"}:
            resource.current_uses = 0

    burning = next(item for item in elian.state.template.spell_save_actions if item.id == "burning-hands")
    shatter = next(item for item in elian.state.template.spell_save_actions if item.id == "shatter")
    fireball = next(item for item in elian.state.template.spell_save_actions if item.id == "fireball")

    assert legal_save_spell_levels(elian.state, "18:elian", burning) == [1]
    assert legal_save_spell_levels(elian.state, "18:elian", shatter) == [2]
    assert available_cast_grant(elian.state, fireball.id, 3) is None


def test_signature_spells_are_independent_free_cast_resources() -> None:
    elian = _member(20)
    fireball = next(item for item in elian.state.template.spell_save_actions if item.id == "fireball")
    lightning = next(item for item in elian.state.template.spell_save_actions if item.id == "lightning-bolt")

    fire_grant, fire_remaining = spend_cast_grant(elian.state, fireball, 3)
    assert fire_grant is not None and fire_remaining == 0
    assert available_cast_grant(elian.state, fireball.id, 3) is None
    assert available_cast_grant(elian.state, lightning.id, 3) is not None
    assert next(item.current_uses for item in elian.state.resources if item.id == "spell-slot-3") == 3


def test_level_twenty_spell_package_keeps_signature_spells_outside_prepared_count() -> None:
    package = build_wizard_2014_spell_package(20, 5)

    assert len(package.spells) == 25
    assert {item.id for item in package.always_prepared_spells} == {
        "fireball", "lightning-bolt",
    }
    assert not ({item.id for item in package.spells} & {"fireball", "lightning-bolt"})


def test_high_level_evoker_audits_are_fully_automated() -> None:
    audits = {
        item.feature_id: item
        for item in build_elian_starweaver_2014_profile(20).feature_audits
    }
    assert audits["overchannel"].automated is True
    assert audits["spell-mastery"].automated is True
    assert audits["signature-spells"].automated is True
