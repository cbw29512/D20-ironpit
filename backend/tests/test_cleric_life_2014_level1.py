from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.canonical_hero_policy import assert_canonical_profile_policy
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.domain.saving_throw_context import SavingThrowContext


def test_2014_seraphine_is_one_cumulative_character() -> None:
    one = build_seraphine_dawnshield_2014_profile(1)
    four = build_seraphine_dawnshield_2014_profile(4)
    eight = build_seraphine_dawnshield_2014_profile(8)
    twenty = build_seraphine_dawnshield_2014_profile(20)
    for profile in (one, four, eight, twenty):
        assert profile.character_name == "Seraphine Dawnshield"
        assert profile.species_id == "hill-dwarf"
        assert profile.background_id == "acolyte"
        assert profile.subclass_id == "life-domain"
        assert profile.base_ability_scores == one.base_ability_scores
        assert profile.species_increases == one.species_increases
    assert one.final_ability_scores.wisdom == 16
    assert four.final_ability_scores.wisdom == 18
    assert eight.final_ability_scores.wisdom == 20
    assert twenty.final_ability_scores.constitution == 20


def test_2014_seraphine_level_one_profile_and_spell_package_are_canonical() -> None:
    profile = build_seraphine_dawnshield_2014_profile(1)
    assert_canonical_profile_policy(profile)
    package = canonical_spell_package("cleric", 1, "2014", 3)
    assert package is not None
    assert [spell.id for spell in package.cantrips] == [
        "guidance", "sacred-flame", "spare-the-dying",
    ]
    assert [spell.id for spell in package.spells] == [
        "healing-word", "guiding-bolt", "shield-of-faith", "inflict-wounds",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == ["bless", "cure-wounds"]


def test_2014_seraphine_level_one_runtime_matches_character_delta() -> None:
    hero = build_seraphine_dawnshield_2014()
    assert hero.level == 1
    assert hero.ruleset == "2014"
    assert hero.ability_scores.model_dump() == {
        "strength": 13, "dexterity": 10, "constitution": 16,
        "intelligence": 8, "wisdom": 16, "charisma": 12,
    }
    assert hero.armor_class == 16
    assert hero.max_hp == 12
    assert hero.speed_ft == 25
    assert hero.weapon_attack.weapon.name == "Warhammer"
    assert hero.weapon_attack.weapon.mastery_property is None
    assert hero.weapon_attack.attack_bonus == 3
    assert hero.weapon_attack.damage_bonus == 1
    assert hero.saving_throw_bonuses["wisdom"] == 5
    assert hero.saving_throw_bonuses["charisma"] == 3
    assert {item.value for item in hero.damage_resistances} == {"poison"}
    assert {item.id: item.max_uses for item in hero.resources} == {"spell-slot-1": 2}


def test_2014_life_cleric_level_one_uses_2014_spell_numbers() -> None:
    hero = build_seraphine_dawnshield_2014()
    sacred = hero.spell_save_actions[0]
    attacks = {item.id: item for item in hero.spell_attack_actions}
    heals = {item.id: item for item in hero.healing_actions}
    assert (sacred.damage_dice_count, sacred.damage_dice_size, sacred.dc) == (1, 8, 13)
    assert (attacks["guiding-bolt"].damage_dice_count, attacks["guiding-bolt"].damage_dice_size) == (4, 6)
    assert (attacks["inflict-wounds"].damage_dice_count, attacks["inflict-wounds"].damage_dice_size) == (3, 10)
    assert (heals["cure-wounds"].dice_count, heals["cure-wounds"].dice_size, heals["cure-wounds"].healing_bonus) == (1, 8, 6)
    assert (heals["healing-word"].dice_count, heals["healing-word"].dice_size, heals["healing-word"].healing_bonus) == (1, 4, 6)


def test_dwarven_resilience_reuses_contextual_poison_save_advantage() -> None:
    state = build_combatant_state(build_seraphine_dawnshield_2014())
    poison, _ = resolve_saving_throw(
        state, "constitution", 99, FixedDiceProvider([2, 18]),
        SavingThrowContext(effect_tags=frozenset({"poison"})),
    )
    assert poison is not None
    assert poison.mode == "advantage"
    assert poison.rolls == [2, 18]

    ordinary_state = build_combatant_state(build_seraphine_dawnshield_2014())
    ordinary, _ = resolve_saving_throw(
        ordinary_state, "constitution", 99, FixedDiceProvider([11]), SavingThrowContext(),
    )
    assert ordinary is not None
    assert ordinary.mode == "normal"
    assert ordinary.rolls == [11]
