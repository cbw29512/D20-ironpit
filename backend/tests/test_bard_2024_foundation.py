from __future__ import annotations

from app.content.audited_bard import build_lyra_silverstring_level
from app.content.audited_bard_profile import build_lyra_silverstring_profile
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.canonical_spell_policy import canonical_spell_package
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.saving_throw_context import SavingThrowContext


def test_2024_bard_level_one_is_legal_support_foundation() -> None:
    profile = build_lyra_silverstring_profile(1)
    hero = build_lyra_silverstring_level(1)

    assert profile.ruleset == "2024"
    assert profile.class_id == "bard"
    assert profile.background_id == "acolyte"
    assert profile.origin_feat_id == "magic-initiate-cleric"
    assert hero.id == "lyra-silverstring-l1"
    assert hero.armor_class == 12
    assert hero.max_hp == 8
    assert hero.weapon_attack is not None
    assert hero.weapon_attack.weapon.id == "dagger"
    assert hero.weapon_attack.weapon.mastery_property is None
    assert {item.id: item.max_uses for item in hero.resources}["bardic-inspiration"] == 3
    assert {item.id: item.max_uses for item in hero.resources}["spell-slot-1"] == 2
    assert [item.id for item in hero.healing_actions] == ["healing-word", "cure-wounds"]


def test_2024_bardic_inspiration_uses_failed_test_universal_grant() -> None:
    hero = build_lyra_silverstring_level(1)
    action = hero.d20_bonus_die_actions[0]

    assert action.id == "bardic-inspiration"
    assert action.action_cost == "bonus_action"
    assert action.range_ft == 60
    assert action.target_mode == "other_ally"
    assert (action.dice_count, action.dice_size) == (1, 6)
    assert set(action.test_kinds) == {"attack", "saving_throw", "ability_check"}
    assert action.duration_rounds == 600
    assert action.exclusive_group == "bardic-inspiration"


def test_2024_bard_level_two_adds_expertise_without_legacy_initiative_bonus() -> None:
    profile = build_lyra_silverstring_profile(2)
    hero = build_lyra_silverstring_level(2)

    assert hero.initiative_bonus == 0
    assert hero.skill_bonuses["acrobatics"] == 4
    assert any(item.feature_id == "expertise" and item.automated for item in profile.feature_audits)
    jack = next(item for item in profile.feature_audits if item.feature_id == "jack-of-all-trades")
    assert jack.combat_relevant is False


def test_2024_bard_foundation_uses_edition_specific_spell_package() -> None:
    level_one = canonical_spell_package("bard", 1, "2024", 3)
    level_two = canonical_spell_package("bard", 2, "2024", 3)

    assert level_one is not None
    assert level_two is not None
    assert [item.id for item in level_one.cantrips] == ["dancing-lights", "mage-hand"]
    assert [item.id for item in level_one.spells] == [
        "healing-word",
        "cure-wounds",
        "detect-magic",
        "comprehend-languages",
    ]
    assert [item.id for item in level_two.spells] == [
        "healing-word",
        "cure-wounds",
        "detect-magic",
        "comprehend-languages",
        "identify",
    ]



def test_2024_lore_bard_level_three_reuses_universal_cutting_words_and_adds_shatter() -> None:
    profile = build_lyra_silverstring_profile(3)
    hero = build_lyra_silverstring_level(3)

    assert profile.subclass_id == "college-lore"
    assert profile.subclass_name == "College of Lore"
    assert hero.max_hp == 18
    assert {item.id: item.max_uses for item in hero.resources}["spell-slot-1"] == 4
    assert {item.id: item.max_uses for item in hero.resources}["spell-slot-2"] == 2

    cutting_words = hero.reaction_roll_penalty_actions[0]
    assert cutting_words.id == "cutting-words"
    assert cutting_words.range_ft == 60
    assert cutting_words.resource_id == "bardic-inspiration"
    assert cutting_words.roll_kinds == ["attack", "ability_check", "damage"]
    assert cutting_words.requires_source_sight is True
    assert cutting_words.requires_target_hearing is False
    assert cutting_words.blocked_target_condition_immunity is None

    shatter = hero.spell_save_actions[0]
    assert shatter.id == "shatter"
    assert shatter.level == 2
    assert shatter.range_ft == 60
    assert shatter.area is not None
    assert (shatter.area.shape, shatter.area.origin, shatter.area.radius_ft) == ("radius", "point", 10)
    assert shatter.save_ability == "constitution"
    assert (shatter.damage_dice_count, shatter.damage_dice_size) == (3, 8)
    assert shatter.damage_type == "thunder"
    assert shatter.success_damage == "half"
    assert shatter.upcast_dice_per_level == 1


def test_2024_bard_level_three_spell_package_adds_shatter() -> None:
    level_three = canonical_spell_package("bard", 3, "2024", 3)

    assert level_three is not None
    assert [item.id for item in level_three.spells] == [
        "healing-word",
        "cure-wounds",
        "detect-magic",
        "comprehend-languages",
        "identify",
        "shatter",
    ]
    shatter = level_three.spells[-1]
    assert (shatter.spell_level, shatter.min_character_level) == (2, 3)



def test_2024_lore_bard_level_four_applies_persistent_charisma_asi() -> None:
    profile = build_lyra_silverstring_profile(4)
    hero = build_lyra_silverstring_level(4)

    assert profile.final_ability_scores.charisma == 19
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [("charisma", 2)]
    assert hero.ability_scores.charisma == 19
    assert hero.max_hp == 23
    assert hero.saving_throw_bonuses["charisma"] == 6
    assert hero.skill_bonuses["performance"] == 6
    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["bardic-inspiration"] == 4
    assert resources["spell-slot-1"] == 4
    assert resources["spell-slot-2"] == 3
    shatter = hero.spell_save_actions[0]
    assert shatter.dc == 14
    assert hero.healing_actions[0].healing_bonus == 4
    assert hero.healing_actions[1].healing_bonus == 4


def test_2024_bard_level_four_spell_package_adds_cantrip_and_utility_spell() -> None:
    level_four = canonical_spell_package("bard", 4, "2024", 4)

    assert level_four is not None
    assert [item.id for item in level_four.cantrips] == [
        "dancing-lights",
        "mage-hand",
        "message",
    ]
    assert [item.id for item in level_four.spells] == [
        "healing-word",
        "cure-wounds",
        "detect-magic",
        "comprehend-languages",
        "identify",
        "shatter",
        "knock",
    ]
    knock = level_four.spells[-1]
    assert (knock.spell_level, knock.min_character_level) == (2, 4)



def test_2024_lore_bard_level_six_reuses_certified_magical_discovery_spells() -> None:
    profile = build_lyra_silverstring_profile(6)
    hero = build_lyra_silverstring_level(6)

    assert hero.max_hp == 33
    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["spell-slot-1"] == 4
    assert resources["spell-slot-2"] == 3
    assert resources["spell-slot-3"] == 3

    magical_discoveries = next(
        item for item in profile.feature_audits
        if item.feature_id == "magical-discoveries"
    )
    assert magical_discoveries.automated is True

    assert [item.id for item in hero.spell_attack_actions] == ["guiding-bolt"]
    guiding_bolt = hero.spell_attack_actions[0]
    assert guiding_bolt.attack_bonus == 7
    assert (
        guiding_bolt.range_ft,
        guiding_bolt.damage_dice_count,
        guiding_bolt.damage_dice_size,
        guiding_bolt.damage_type,
    ) == (120, 4, 6, "radiant")

    assert [item.id for item in hero.defensive_spell_actions] == ["bless"]
    bless = hero.defensive_spell_actions[0]
    assert bless.concentration is True
    assert bless.target_count == 3

    assert [item.id for item in hero.effect_removal_actions] == ["dispel-magic"]
    dispel = hero.effect_removal_actions[0]
    assert dispel.casting_ability == "charisma"
    assert dispel.range_ft == 120
    assert dispel.resource_id == "spell-slot-3"


def test_2024_bard_level_six_spell_package_keeps_discoveries_always_prepared() -> None:
    level_six = canonical_spell_package("bard", 6, "2024", 4)

    assert level_six is not None
    assert len(level_six.spells) == 10
    assert level_six.spells[-1].id == "dispel-magic"
    assert [item.id for item in level_six.always_prepared_spells] == [
        "bless",
        "guiding-bolt",
    ]



def _bard7_countercharm_setup():
    source = EncounterCombatant(
        combatant_id="lyra-7",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_lyra_silverstring_level(7)),
    )
    target = EncounterCombatant(
        combatant_id="lyra-1",
        side="heroes",
        position_ft=25,
        state=build_combatant_state(build_lyra_silverstring_level(1)),
    )
    enemy = EncounterCombatant(
        combatant_id="enemy",
        side="monsters",
        position_ft=50,
        state=build_combatant_state(build_lyra_silverstring_level(1)),
    )
    setup = EncounterSetup(
        heroes=[source, target],
        monsters=[enemy],
        hero_total_levels=8,
        monster_total_cr="1",
    )
    return source, target, setup


def test_2024_bard_level_seven_countercharm_rerolls_matching_failed_save_with_advantage() -> None:
    source, target, setup = _bard7_countercharm_setup()

    roll, succeeded = resolve_saving_throw(
        target.state,
        "charisma",
        20,
        FixedDiceProvider([1, 3, 18]),
        SavingThrowContext(effect_tags=frozenset({"charmed"})),
        encounter_roller=target,
        setup=setup,
    )

    assert succeeded is True
    assert roll is not None
    assert roll.selected_roll == 18
    assert roll.revisions[-1].source_effect_id == "countercharm"
    assert "Countercharm" in roll.notation
    assert source.state.reaction_available is False


def test_2024_bard_level_seven_countercharm_ignores_nonmatching_failed_save() -> None:
    source, target, setup = _bard7_countercharm_setup()

    roll, succeeded = resolve_saving_throw(
        target.state,
        "charisma",
        20,
        FixedDiceProvider([1]),
        SavingThrowContext(effect_tags=frozenset({"poison"})),
        encounter_roller=target,
        setup=setup,
    )

    assert succeeded is False
    assert roll is not None
    assert not roll.revisions
    assert source.state.reaction_available is True


def test_2024_bard_level_seven_spell_package_adds_greater_invisibility() -> None:
    level_seven = canonical_spell_package("bard", 7, "2024", 4)

    assert level_seven is not None
    assert len(level_seven.spells) == 11
    assert level_seven.spells[-1].id == "greater-invisibility"
    assert [item.id for item in level_seven.always_prepared_spells] == [
        "bless",
        "guiding-bolt",
    ]

    hero = build_lyra_silverstring_level(7)
    greater = next(item for item in hero.defensive_spell_actions if item.id == "greater-invisibility")
    assert (
        greater.level,
        greater.action_cost,
        greater.range_ft,
        greater.duration_minutes,
        greater.target_count,
        greater.condition_ids,
        greater.concentration,
    ) == (4, "action", 5, 1, 1, ["invisible"], True)



def test_2024_lore_bard_level_eight_applies_split_asi_and_derived_values() -> None:
    profile = build_lyra_silverstring_profile(8)
    hero = build_lyra_silverstring_level(8)

    assert (profile.final_ability_scores.charisma, profile.final_ability_scores.wisdom) == (20, 16)
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("charisma", 2),
        ("charisma", 1),
        ("wisdom", 1),
    ]
    asi = next(
        item for item in profile.feature_audits
        if item.feature_id == "ability-score-improvement-8"
    )
    assert asi.automated is True

    assert hero.max_hp == 43
    assert hero.ability_scores.charisma == 20
    assert hero.ability_scores.wisdom == 16
    assert hero.saving_throw_bonuses["charisma"] == 8
    assert hero.skill_bonuses["performance"] == 8
    assert hero.skill_bonuses["perception"] == 6
    assert hero.skill_bonuses["insight"] == 6

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["bardic-inspiration"] == 5
    assert resources["spell-slot-1"] == 4
    assert resources["spell-slot-2"] == 3
    assert resources["spell-slot-3"] == 3
    assert resources["spell-slot-4"] == 2

    shatter = next(item for item in hero.spell_save_actions if item.id == "shatter")
    assert shatter.dc == 16
    guiding_bolt = next(item for item in hero.spell_attack_actions if item.id == "guiding-bolt")
    assert guiding_bolt.attack_bonus == 8
    assert hero.healing_actions[0].healing_bonus == 5
    assert hero.healing_actions[1].healing_bonus == 5


def test_2024_bard_level_eight_spell_package_adds_arena_neutral_tongues() -> None:
    level_eight = canonical_spell_package("bard", 8, "2024", 5)

    assert level_eight is not None
    assert len(level_eight.spells) == 12
    assert level_eight.spells[-1].id == "tongues"
    assert level_eight.spells[-1].role == "utility"
    assert level_eight.spells[-1].required_capabilities == ["arena-out-of-scope"]
    assert [item.id for item in level_eight.always_prepared_spells] == [
        "bless",
        "guiding-bolt",
    ]

def test_2024_lore_bard_level_nine_applies_expertise_and_fifth_level_healing() -> None:
    profile = build_lyra_silverstring_profile(9)
    hero = build_lyra_silverstring_level(9)

    assert hero.max_hp == 48
    assert hero.skill_bonuses["acrobatics"] == 8
    assert hero.skill_bonuses["perception"] == 11
    assert hero.skill_bonuses["performance"] == 13

    expertise = next(
        item for item in profile.feature_audits
        if item.feature_id == "expertise-9"
    )
    assert expertise.automated is True

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["bardic-inspiration"] == 5
    assert resources["adrenaline-rush"] == 4
    assert resources["spell-slot-1"] == 4
    assert resources["spell-slot-2"] == 3
    assert resources["spell-slot-3"] == 3
    assert resources["spell-slot-4"] == 3
    assert resources["spell-slot-5"] == 1

    mass = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds")
    assert (
        mass.action_cost,
        mass.range_ft,
        mass.max_targets,
        mass.area_radius_ft,
        mass.dice_count,
        mass.dice_size,
        mass.healing_bonus,
        mass.resource_id,
    ) == ("action", 60, 6, 30, 5, 8, 5, "spell-slot-5")


def test_2024_bard_level_nine_spell_package_adds_edition_correct_fifth_level_spells() -> None:
    level_nine = canonical_spell_package("bard", 9, "2024", 5)

    assert level_nine is not None
    assert len(level_nine.spells) == 14
    assert [item.id for item in level_nine.spells[-2:]] == [
        "mass-cure-wounds",
        "raise-dead",
    ]
    mass, raise_dead = level_nine.spells[-2:]
    assert (mass.spell_level, mass.min_character_level) == (5, 9)
    assert mass.required_capabilities == ["healing"]
    assert (raise_dead.spell_level, raise_dead.min_character_level) == (5, 9)
    assert raise_dead.required_capabilities == ["arena-out-of-scope"]
    assert [item.id for item in level_nine.always_prepared_spells] == [
        "bless",
        "guiding-bolt",
    ]

def test_2024_lore_bard_level_ten_scales_inspiration_and_adds_fireball() -> None:
    profile = build_lyra_silverstring_profile(10)
    hero = build_lyra_silverstring_level(10)

    assert hero.max_hp == 53
    magical_secrets = next(
        item for item in profile.feature_audits
        if item.feature_id == "magical-secrets"
    )
    assert magical_secrets.automated is True

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["bardic-inspiration"] == 5
    assert resources["adrenaline-rush"] == 4
    assert resources["spell-slot-1"] == 4
    assert resources["spell-slot-2"] == 3
    assert resources["spell-slot-3"] == 3
    assert resources["spell-slot-4"] == 3
    assert resources["spell-slot-5"] == 2

    inspiration = hero.d20_bonus_die_actions[0]
    assert (inspiration.id, inspiration.dice_count, inspiration.dice_size) == (
        "bardic-inspiration",
        1,
        10,
    )
    cutting_words = hero.reaction_roll_penalty_actions[0]
    assert (cutting_words.id, cutting_words.dice_count, cutting_words.dice_size) == (
        "cutting-words",
        1,
        10,
    )

    fireball = next(item for item in hero.spell_save_actions if item.id == "fireball")
    assert fireball.dc == 17
    assert fireball.level == 3
    assert fireball.action_cost == "action"
    assert fireball.range_ft == 150
    assert fireball.area is not None
    assert (
        fireball.area.shape,
        fireball.area.origin,
        fireball.area.radius_ft,
    ) == ("radius", "point", 20)
    assert fireball.save_ability == "dexterity"
    assert (
        fireball.damage_dice_count,
        fireball.damage_dice_size,
        fireball.damage_type,
        fireball.success_damage,
        fireball.upcast_dice_per_level,
    ) == (8, 6, "fire", "half", 1)


def test_2024_bard_level_ten_spell_package_uses_magical_secrets_without_new_engine() -> None:
    level_ten = canonical_spell_package("bard", 10, "2024", 5)

    assert level_ten is not None
    assert len(level_ten.cantrips) == 4
    assert level_ten.cantrips[-1].id == "prestidigitation"
    assert level_ten.cantrips[-1].required_capabilities == ["arena-out-of-scope"]
    assert len(level_ten.spells) == 15
    assert level_ten.spells[-1].id == "fireball"
    assert level_ten.spells[-1].required_capabilities == [
        "save-damage",
        "area",
        "magical-secrets",
    ]
    assert [item.id for item in level_ten.always_prepared_spells] == [
        "bless",
        "guiding-bolt",
    ]


def test_2024_lore_bard_level_eleven_adds_sixth_level_magical_secret() -> None:
    hero = build_lyra_silverstring_level(11)

    assert hero.max_hp == 58
    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["bardic-inspiration"] == 5
    assert resources["spell-slot-5"] == 2
    assert resources["spell-slot-6"] == 1

    disintegrate = next(item for item in hero.spell_save_actions if item.id == "disintegrate")
    assert disintegrate.dc == 17
    assert (
        disintegrate.level,
        disintegrate.action_cost,
        disintegrate.range_ft,
        disintegrate.save_ability,
        disintegrate.damage_dice_count,
        disintegrate.damage_dice_size,
        disintegrate.damage_bonus,
        disintegrate.damage_type,
        disintegrate.success_damage,
        disintegrate.upcast_dice_per_level,
    ) == (6, "action", 60, "dexterity", 10, 6, 40, "force", "none", 3)


def test_2024_bard_level_eleven_spell_package_uses_magical_secrets_for_disintegrate() -> None:
    level_eleven = canonical_spell_package("bard", 11, "2024", 6)

    assert level_eleven is not None
    assert len(level_eleven.cantrips) == 4
    assert len(level_eleven.spells) == 16
    assert level_eleven.spells[-1].id == "disintegrate"
    assert level_eleven.spells[-1].spell_level == 6
    assert level_eleven.spells[-1].required_capabilities == [
        "save-damage",
        "magical-secrets",
    ]
    assert [item.id for item in level_eleven.always_prepared_spells] == [
        "bless",
        "guiding-bolt",
    ]


def test_2024_lore_bard_level_twelve_applies_wisdom_asi() -> None:
    profile = build_lyra_silverstring_profile(12)
    hero = build_lyra_silverstring_level(12)

    assert hero.max_hp == 63
    assert (profile.final_ability_scores.charisma, profile.final_ability_scores.wisdom) == (20, 18)
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("charisma", 2),
        ("charisma", 1),
        ("wisdom", 1),
        ("wisdom", 2),
    ]
    asi = next(
        item for item in profile.feature_audits
        if item.feature_id == "ability-score-improvement-12"
    )
    assert asi.automated is True

    assert hero.skill_bonuses["perception"] == 12
    assert hero.skill_bonuses["insight"] == 8
    assert hero.saving_throw_bonuses["wisdom"] == 4

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["spell-slot-5"] == 2
    assert resources["spell-slot-6"] == 1

    disintegrate = next(item for item in hero.spell_save_actions if item.id == "disintegrate")
    assert disintegrate.dc == 17

    level_twelve = canonical_spell_package("bard", 12, "2024", 6)
    assert level_twelve is not None
    assert len(level_twelve.cantrips) == 4
    assert len(level_twelve.spells) == 16


def test_2024_lore_bard_level_thirteen_adds_seventh_level_magical_secret() -> None:
    profile = build_lyra_silverstring_profile(13)
    hero = build_lyra_silverstring_level(13)

    assert hero.max_hp == 68
    assert hero.ability_scores.wisdom == 18
    assert hero.ability_scores.charisma == 20
    assert hero.skill_bonuses["perception"] == 14
    assert hero.skill_bonuses["performance"] == 15

    spell_audit = next(
        item for item in profile.feature_audits
        if item.feature_id == "bard-combat-spells-7"
    )
    assert spell_audit.automated is True

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["adrenaline-rush"] == 5
    assert resources["spell-slot-6"] == 1
    assert resources["spell-slot-7"] == 1

    finger = next(item for item in hero.spell_save_actions if item.id == "finger-of-death")
    assert finger.dc == 18
    assert (
        finger.level,
        finger.action_cost,
        finger.range_ft,
        finger.save_ability,
        finger.damage_dice_count,
        finger.damage_dice_size,
        finger.damage_bonus,
        finger.damage_type,
        finger.success_damage,
    ) == (7, "action", 60, "constitution", 7, 8, 30, "necrotic", "half")


def test_2024_bard_level_thirteen_spell_package_adds_finger_of_death() -> None:
    level_thirteen = canonical_spell_package("bard", 13, "2024", 7)

    assert level_thirteen is not None
    assert len(level_thirteen.cantrips) == 4
    assert len(level_thirteen.spells) == 17
    assert level_thirteen.spells[-1].id == "finger-of-death"
    assert level_thirteen.spells[-1].spell_level == 7
    assert level_thirteen.spells[-1].required_capabilities == [
        "save-damage",
        "magical-secrets",
    ]


def test_2024_lore_bard_level_fifteen_scales_inspiration_and_adds_sunburst() -> None:
    profile = build_lyra_silverstring_profile(15)
    hero = build_lyra_silverstring_level(15)

    assert hero.max_hp == 78
    audit = next(item for item in profile.feature_audits if item.feature_id == "bard-combat-spells-8")
    assert audit.automated is True

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["spell-slot-8"] == 1

    inspiration = hero.d20_bonus_die_actions[0]
    assert (inspiration.dice_count, inspiration.dice_size) == (1, 12)
    cutting_words = hero.reaction_roll_penalty_actions[0]
    assert (cutting_words.dice_count, cutting_words.dice_size) == (1, 12)
    peerless = hero.progression_features.resource_backed_d20_bonus_dice[0]
    assert peerless.dice_size == 12

    sunburst = next(item for item in hero.spell_save_actions if item.id == "sunburst")
    assert sunburst.dc == 18
    assert sunburst.area is not None
    assert (sunburst.area.shape, sunburst.area.origin, sunburst.area.radius_ft) == ("radius", "point", 60)
    assert (sunburst.damage_dice_count, sunburst.damage_dice_size, sunburst.damage_type) == (12, 6, "radiant")
    assert sunburst.success_damage == "half"
    rider = sunburst.failed_save_timed_effect
    assert rider is not None
    assert rider.effect_id == "blinded"
    assert rider.repeat_save_timing == "target_turn_end"


def test_2024_bard_level_fifteen_spell_package_adds_sunburst() -> None:
    level_fifteen = canonical_spell_package("bard", 15, "2024", 8)

    assert level_fifteen is not None
    assert len(level_fifteen.spells) == 18
    assert level_fifteen.spells[-1].id == "sunburst"
    assert level_fifteen.spells[-1].spell_level == 8
    assert level_fifteen.spells[-1].required_capabilities == [
        "save-damage",
        "area",
        "condition",
        "magical-secrets",
    ]


def test_2024_lore_bard_level_sixteen_applies_final_wisdom_asi() -> None:
    profile = build_lyra_silverstring_profile(16)
    hero = build_lyra_silverstring_level(16)

    assert hero.max_hp == 83
    assert (profile.final_ability_scores.charisma, profile.final_ability_scores.wisdom) == (20, 20)
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [
        ("charisma", 2),
        ("charisma", 1),
        ("wisdom", 1),
        ("wisdom", 2),
        ("wisdom", 2),
    ]
    asi = next(
        item for item in profile.feature_audits
        if item.feature_id == "ability-score-improvement-16"
    )
    assert asi.automated is True

    assert hero.skill_bonuses["perception"] == 15
    assert hero.skill_bonuses["insight"] == 10
    assert hero.saving_throw_bonuses["wisdom"] == 5

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["spell-slot-8"] == 1
    assert "spell-slot-9" not in resources

    level_sixteen = canonical_spell_package("bard", 16, "2024", 8)
    assert level_sixteen is not None
    assert len(level_sixteen.spells) == 18


def test_2024_lore_bard_level_seventeen_adds_power_word_kill() -> None:
    from app.combat.hp_threshold_instant_death import (
        choose_hp_threshold_instant_death,
        resolve_hp_threshold_instant_death,
    )
    from app.content.monsters import build_commoner
    from app.domain.grid import GridPosition

    profile = build_lyra_silverstring_profile(17)
    hero = build_lyra_silverstring_level(17)

    assert hero.max_hp == 88
    assert hero.ability_scores.wisdom == 20
    assert hero.ability_scores.charisma == 20
    assert hero.skill_bonuses["perception"] == 17
    assert hero.skill_bonuses["performance"] == 17

    audit = next(item for item in profile.feature_audits if item.feature_id == "bard-combat-spells-9")
    assert audit.automated is True

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["spell-slot-9"] == 1

    action = hero.hp_threshold_instant_death_actions[0]
    assert (
        action.id,
        action.range_ft,
        action.max_current_hp,
        action.fallback_damage_dice_count,
        action.fallback_damage_dice_size,
        action.fallback_damage_type,
        action.resource_id,
    ) == ("power-word-kill", 60, 100, 12, 12, "psychic", "spell-slot-9")

    source = EncounterCombatant(
        combatant_id="lyra-17", side="heroes", position_ft=0,
        state=build_combatant_state(hero),
    )
    target_template = build_commoner().model_copy(update={"max_hp": 200})
    target = EncounterCombatant(
        combatant_id="target", side="monsters", position_ft=30,
        state=build_combatant_state(target_template),
    )
    target.state.position = GridPosition(x=6, y=0)
    source.state.position = GridPosition(x=0, y=0)
    setup = EncounterSetup(
        heroes=[source], monsters=[target], hero_total_levels=17, monster_total_cr="0",
    )

    target.state.current_hp = 150
    selected = choose_hp_threshold_instant_death(source, setup)
    assert selected is not None
    event = resolve_hp_threshold_instant_death(
        1, 1, source, target, selected[1], setup,
        dice=FixedDiceProvider([1] * 12),
    )
    assert event.damage_roll is not None and event.damage_roll.total == 12
    assert target.state.current_hp == 138
    assert target.state.is_dead is False


def test_2024_power_word_kill_uses_death_threshold_at_one_hundred_hp() -> None:
    from app.combat.hp_threshold_instant_death import resolve_hp_threshold_instant_death
    from app.content.monsters import build_commoner

    hero = build_lyra_silverstring_level(17)
    source = EncounterCombatant(
        combatant_id="lyra-17", side="heroes", position_ft=0,
        state=build_combatant_state(hero),
    )
    target_template = build_commoner().model_copy(update={"max_hp": 200})
    target = EncounterCombatant(
        combatant_id="target", side="monsters", position_ft=30,
        state=build_combatant_state(target_template),
    )
    target.state.current_hp = 100
    setup = EncounterSetup(
        heroes=[source], monsters=[target], hero_total_levels=17, monster_total_cr="0",
    )
    action = hero.hp_threshold_instant_death_actions[0]

    event = resolve_hp_threshold_instant_death(
        1, 1, source, target, action, setup,
        dice=FixedDiceProvider([12] * 12),
    )

    assert event.damage_roll is None
    assert target.state.is_dead is True
    assert target.state.current_hp == 0


def test_2024_bard_level_seventeen_spell_package_adds_power_word_kill() -> None:
    level_seventeen = canonical_spell_package("bard", 17, "2024", 9)

    assert level_seventeen is not None
    assert len(level_seventeen.spells) == 19
    assert level_seventeen.spells[-1].id == "power-word-kill"
    assert level_seventeen.spells[-1].spell_level == 9
    assert level_seventeen.spells[-1].required_capabilities == [
        "hp-threshold-instant-death",
        "fallback-damage",
        "magical-secrets",
    ]


def test_2024_lore_bard_level_eighteen_superior_inspiration_restores_to_two() -> None:
    from app.combat.initiative_resource_refill import resolve_initiative_resource_refills

    profile = build_lyra_silverstring_profile(18)
    hero = build_lyra_silverstring_level(18)

    assert hero.max_hp == 93
    audit = next(item for item in profile.feature_audits if item.feature_id == "superior-inspiration")
    assert audit.automated is True

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["spell-slot-5"] == 3
    assert resources["spell-slot-9"] == 1

    grant = hero.initiative_resource_refill_grants[0]
    assert (
        grant.source_id,
        grant.resource_id,
        grant.when_at_or_below,
        grant.restore_to_minimum,
    ) == ("superior-inspiration", "bardic-inspiration", 1, 2)

    source = EncounterCombatant(
        combatant_id="lyra-18", side="heroes", position_ft=0,
        state=build_combatant_state(hero),
    )
    enemy = EncounterCombatant(
        combatant_id="enemy", side="monsters", position_ft=30,
        state=build_combatant_state(build_lyra_silverstring_level(1)),
    )
    setup = EncounterSetup(
        heroes=[source], monsters=[enemy], hero_total_levels=18, monster_total_cr="1",
    )
    inspiration = next(item for item in source.state.resources if item.id == "bardic-inspiration")

    inspiration.current_uses = 0
    events, _ = resolve_initiative_resource_refills(1, setup)
    assert inspiration.current_uses == 2
    assert events[0].resource_remaining == 2

    inspiration.current_uses = 1
    events, _ = resolve_initiative_resource_refills(2, setup)
    assert inspiration.current_uses == 2
    assert events[0].resource_remaining == 2

    inspiration.current_uses = 2
    events, _ = resolve_initiative_resource_refills(3, setup)
    assert inspiration.current_uses == 2
    assert events == []


def test_2024_bard_level_eighteen_spell_package_adds_teleport() -> None:
    level_eighteen = canonical_spell_package("bard", 18, "2024", 9)

    assert level_eighteen is not None
    assert len(level_eighteen.spells) == 20
    assert level_eighteen.spells[-1].id == "teleport"
    assert level_eighteen.spells[-1].spell_level == 7
    assert level_eighteen.spells[-1].required_capabilities == ["arena-out-of-scope"]


def test_2024_lore_bard_level_nineteen_uses_raw_boon_of_fate() -> None:
    profile = build_lyra_silverstring_profile(19)
    hero = build_lyra_silverstring_level(19)

    assert hero.max_hp == 98
    assert (hero.ability_scores.intelligence, hero.ability_scores.wisdom, hero.ability_scores.charisma) == (14, 20, 20)
    assert [(item.ability, item.amount) for item in profile.advancement_increases][-1] == ("intelligence", 1)

    audit = next(item for item in profile.feature_audits if item.feature_id == "boon-of-fate")
    assert audit.automated is True

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["spell-slot-6"] == 2
    assert resources["boon-of-fate"] == 1

    grants = hero.progression_features.resource_backed_d20_outcome_adjustments
    assert len(grants) == 1
    grant = grants[0]
    assert (
        grant.source_id,
        grant.resource_id,
        grant.dice_count,
        grant.dice_size,
        grant.range_ft,
        grant.test_kinds,
        grant.can_add,
        grant.can_subtract,
    ) == (
        "boon-of-fate",
        "boon-of-fate",
        2,
        4,
        60,
        ["attack", "saving_throw", "ability_check"],
        True,
        True,
    )

    refills = {item.source_id: item for item in hero.initiative_resource_refill_grants}
    assert set(refills) == {"superior-inspiration", "boon-of-fate"}
    assert refills["boon-of-fate"].resource_id == "boon-of-fate"
    assert refills["boon-of-fate"].restore_to_max is True


def test_2024_bard_level_nineteen_adds_cone_of_cold_through_magical_secrets() -> None:
    hero = build_lyra_silverstring_level(19)
    cone = next(item for item in hero.spell_save_actions if item.id == "cone-of-cold")

    assert cone.dc == 19
    assert cone.area is not None
    assert (
        cone.level,
        cone.action_cost,
        cone.range_ft,
        cone.area.shape,
        cone.area.origin,
        cone.area.length_ft,
        cone.save_ability,
        cone.damage_dice_count,
        cone.damage_dice_size,
        cone.damage_type,
        cone.success_damage,
        cone.upcast_dice_per_level,
    ) == (5, "action", 60, "cone", "self", 60, "constitution", 8, 8, "cold", "half", 1)

    level_nineteen = canonical_spell_package("bard", 19, "2024", 9)
    assert level_nineteen is not None
    assert len(level_nineteen.spells) == 21
    assert level_nineteen.spells[-1].id == "cone-of-cold"
    assert level_nineteen.spells[-1].required_capabilities == [
        "save-damage",
        "area",
        "magical-secrets",
    ]
