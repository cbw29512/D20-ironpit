from app.combat.dice import FixedDiceProvider
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.spell_attack_sequence import resolve_spell_attack_sequence
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import begin_turn, build_combatant_state
from app.combat.targeted_concentration_damage import resolve_targeted_concentration_damage
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup

from app.content.warlock_2014_progression import warlock_2014_level
from app.content.warlock_fiend_2014_profile import build_varek_ashenmark_2014_profile
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014


def test_2014_warlock_progression_uses_edition_correct_pact_magic() -> None:
    assert warlock_2014_level(1).pact_slots == 1
    assert warlock_2014_level(1).pact_slot_level == 1
    assert warlock_2014_level(1).invocations_known == 0
    assert warlock_2014_level(2).invocations_known == 2
    assert warlock_2014_level(3).pact_slot_level == 2
    assert warlock_2014_level(11).pact_slots == 3
    assert warlock_2014_level(17).pact_slots == 4
    assert warlock_2014_level(20).pact_slot_level == 5
    assert warlock_2014_level(17).mystic_arcanum_levels == (6, 7, 8, 9)


def test_varek_level_one_is_a_fiend_blaster_not_2024_warlock_data() -> None:
    profile = build_varek_ashenmark_2014_profile(1)
    varek = build_varek_ashenmark_2014(1)

    assert profile.ruleset == "2014"
    assert profile.subclass_id == "fiend-patron"
    assert profile.build_id == "eldritch-blaster"
    assert varek.ruleset == "2014"
    assert varek.level == 1
    assert varek.armor_class == 13
    assert varek.max_hp == 10

    resources = {item.id: item.max_uses for item in varek.resources}
    assert resources == {"spell-slot-1": 1}

    blast = varek.spell_attack_actions[0]
    assert blast.id == "eldritch-blast"
    assert blast.range_ft == 120
    assert blast.damage_dice_count == 1
    assert blast.damage_dice_size == 10
    assert blast.damage_type == "force"
    assert blast.damage_bonus == 0

    blessing = varek.progression_features.source_reduces_hostile_to_zero_hp_temporary_hp
    assert blessing is not None
    assert blessing.source_id == "dark-ones-blessing"
    assert blessing.ability == "charisma"
    assert blessing.per_level == 1


def test_varek_level_one_hex_is_bound_to_the_shared_damage_primitive() -> None:
    profile = build_varek_ashenmark_2014_profile(1)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["hex"].combat_relevant is True
    assert audits["hex"].automated is True
    assert "Hunter's Mark" in audits["hex"].notes


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _commoner_2014():
    return build_commoner().model_copy(update={
        "ruleset": "2014", "max_hp": 30,
        "saving_throw_bonuses": {
            "strength": 0, "dexterity": 0, "constitution": 0,
            "intelligence": 0, "wisdom": 0, "charisma": 0,
        },
    })


def test_hex_then_eldritch_blast_uses_one_slot_and_adds_necrotic_damage() -> None:
    varek = _member(build_varek_ashenmark_2014(1), "varek", "heroes", 0)
    enemy = _member(_commoner_2014(), "enemy", "monsters", 30)
    setup = EncounterSetup(
        heroes=[varek], monsters=[enemy], hero_total_levels=1, monster_total_cr="0", ruleset="2014",
    )
    begin_turn(varek.state)

    hex_event = resolve_targeted_concentration_damage(1, 1, varek, setup, "1:varek")

    assert hex_event is not None and hex_event.feature_id == "hex"
    assert varek.state.bonus_action_available is False
    assert varek.state.action_available is True
    assert varek.state.concentration is not None and varek.state.concentration.effect_id == "hex"
    assert next(item.current_uses for item in varek.state.resources if item.id == "spell-slot-1") == 0
    rider = next(item for item in varek.state.active_modifiers if item.source_effect_id == "hex")
    assert rider.target_id == "enemy"
    assert rider.dice_count == 1 and rider.dice_size == 6
    assert rider.damage_type.value == "necrotic"

    blast = varek.state.template.spell_attack_actions[0]
    event = resolve_spell_attack(
        2, 1, varek, enemy, blast, setup, "1:varek", FixedDiceProvider([15, 7, 4]),
    )

    assert event.hit is True
    assert event.damage_roll is not None and event.damage_roll.total == 11
    assert [item.source for item in event.damage_components] == ["Eldritch Blast", "Hex"]
    assert [item.damage_type.value for item in event.damage_components] == ["force", "necrotic"]


def test_hex_retargets_after_zero_without_spending_another_slot() -> None:
    varek = _member(build_varek_ashenmark_2014(1), "varek", "heroes", 0)
    first = _member(_commoner_2014(), "first", "monsters", 30)
    second = _member(_commoner_2014(), "second", "monsters", 35)
    setup = EncounterSetup(
        heroes=[varek], monsters=[first, second], hero_total_levels=1, monster_total_cr="0", ruleset="2014",
    )
    begin_turn(varek.state)
    assert resolve_targeted_concentration_damage(1, 1, varek, setup, "1:varek") is not None
    first.state.current_hp = 0
    first.state.is_alive = False
    first.state.is_dead = True

    begin_turn(varek.state)
    moved = resolve_targeted_concentration_damage(2, 2, varek, setup, "2:varek")

    assert moved is not None and moved.resource_remaining is None
    assert "moves Hex" in moved.description
    assert varek.state.concentration is not None and varek.state.concentration.effect_id == "hex"
    assert next(item.current_uses for item in varek.state.resources if item.id == "spell-slot-1") == 0
    rider = next(item for item in varek.state.active_modifiers if item.source_effect_id == "hex")
    assert rider.target_id == "second"


def test_varek_level_two_prioritizes_simple_blaster_invocations() -> None:
    profile = build_varek_ashenmark_2014_profile(2)
    varek = build_varek_ashenmark_2014(2)

    assert profile.level == 2
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["agonizing-blast"].automated is True
    assert audits["eldritch-spear"].automated is True

    resources = {item.id: item.max_uses for item in varek.resources}
    assert resources == {"spell-slot-1": 2}

    blast = next(item for item in varek.spell_attack_actions if item.id == "eldritch-blast")
    assert blast.attack_bonus == 5
    assert blast.damage_bonus == 3
    assert blast.range_ft == 300


def test_varek_level_two_spell_package_avoids_forcing_new_damage_subsystems() -> None:
    from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package

    package = build_warlock_2014_spell_package(2)
    assert [item.id for item in package.cantrips] == ["eldritch-blast", "poison-spray"]
    assert [item.id for item in package.spells] == ["hex", "burning-hands", "comprehend-languages"]


def test_varek_level_three_tome_and_pact_magic() -> None:
    from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package

    profile = build_varek_ashenmark_2014_profile(3)
    varek = build_varek_ashenmark_2014(3)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert profile.level == 3
    assert audits["pact-of-the-tome"].automated is True
    assert audits["pact-of-the-tome"].combat_relevant is False
    assert {item.id: item.max_uses for item in varek.resources} == {"spell-slot-2": 2}
    assert [item.id for item in varek.spell_attack_actions] == ["eldritch-blast", "scorching-ray"]
    assert [item.id for item in varek.spell_save_actions] == ["poison-spray", "burning-hands", "shatter"]

    package = build_warlock_2014_spell_package(3)
    assert [item.id for item in package.spells] == [
        "hex", "burning-hands", "scorching-ray", "shatter",
    ]



def test_scorching_ray_sequence_spends_one_pact_slot_and_hexes_each_hit() -> None:
    varek = _member(build_varek_ashenmark_2014(3), "varek", "heroes", 0)
    enemy = _member(_commoner_2014(), "enemy", "monsters", 30)
    enemy.state.template.max_hp = 100
    enemy.state.current_hp = 100
    setup = EncounterSetup(
        heroes=[varek], monsters=[enemy], hero_total_levels=3, monster_total_cr="0", ruleset="2014",
    )

    begin_turn(varek.state)
    assert resolve_targeted_concentration_damage(1, 1, varek, setup, "1:varek") is not None
    assert next(item.current_uses for item in varek.state.resources if item.id == "spell-slot-2") == 1

    begin_turn(varek.state)
    ray = next(item for item in varek.state.template.spell_attack_actions if item.id == "scorching-ray")
    events, sequence = resolve_spell_attack_sequence(
        2, 2, varek, enemy, ray, setup, "2:varek",
        FixedDiceProvider([
            15, 4, 5, 3,
            16, 6, 2, 4,
            17, 5, 5, 2,
        ]),
        slot_level=2,
    )

    ray_events = [event for event in events if event.feature_id == "scorching-ray"]
    assert len(ray_events) == 3
    assert sequence == 5
    assert varek.state.action_available is False
    assert next(item.current_uses for item in varek.state.resources if item.id == "spell-slot-2") == 0
    assert all([part.source for part in event.damage_components] == ["Scorching Ray", "Hex"] for event in ray_events)
    assert all([part.damage_type.value for part in event.damage_components] == ["fire", "necrotic"] for event in ray_events)


def test_eldritch_blast_beam_scaling_uses_independent_attacks() -> None:
    from app.content.warlock_2014_spells import eldritch_blast_2014

    assert eldritch_blast_2014(7, 4, damage_bonus=4).attack_count == 1
    assert eldritch_blast_2014(7, 5, damage_bonus=4).attack_count == 2
    assert eldritch_blast_2014(9, 11, damage_bonus=5).attack_count == 3
    assert eldritch_blast_2014(11, 17, damage_bonus=5).attack_count == 4



def test_varek_level_four_raises_charisma_for_blaster_damage() -> None:
    from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package

    profile = build_varek_ashenmark_2014_profile(4)
    varek = build_varek_ashenmark_2014(4)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert profile.final_ability_scores.charisma == 18
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [("charisma", 2)]
    assert audits["ability-score-improvement-l4"].automated is True

    blast = next(item for item in varek.spell_attack_actions if item.id == "eldritch-blast")
    assert blast.attack_bonus == 6
    assert blast.damage_bonus == 4
    assert blast.range_ft == 300
    assert {item.id: item.max_uses for item in varek.resources} == {"spell-slot-2": 2}

    package = build_warlock_2014_spell_package(4)
    assert [item.id for item in package.cantrips] == ["eldritch-blast", "poison-spray", "mage-hand"]
    assert [item.id for item in package.spells] == [
        "hex", "burning-hands", "scorching-ray", "shatter", "comprehend-languages",
    ]



def test_varek_level_five_unlocks_core_blaster_power_spike() -> None:
    from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package

    profile = build_varek_ashenmark_2014_profile(5)
    varek = build_varek_ashenmark_2014(5)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["eldritch-blast-second-beam"].automated is True
    assert audits["mask-of-many-faces"].combat_relevant is False
    assert {item.id: item.max_uses for item in varek.resources} == {"spell-slot-3": 2}

    blast = next(item for item in varek.spell_attack_actions if item.id == "eldritch-blast")
    rays = next(item for item in varek.spell_attack_actions if item.id == "scorching-ray")
    assert blast.attack_count == 2
    assert blast.attack_bonus == 7
    assert blast.damage_bonus == 4
    assert rays.attack_count_at_slot(3) == 4
    assert "fireball" in [item.id for item in varek.spell_save_actions]

    package = build_warlock_2014_spell_package(5)
    assert len(package.spells) == 6
    assert package.spells[-1].id == "fireball"



def test_varek_level_six_reuses_d20_bonus_and_dispel() -> None:
    from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package

    profile = build_varek_ashenmark_2014_profile(6)
    varek = build_varek_ashenmark_2014(6)
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["dark-ones-own-luck"].automated is True
    assert audits["dispel-magic"].automated is True

    resources = {item.id: item.max_uses for item in varek.resources}
    assert resources == {"spell-slot-3": 2, "dark-ones-own-luck": 1}
    assert [item.id for item in varek.effect_removal_actions] == ["dispel-magic"]

    rule = varek.progression_features.resource_backed_d20_bonus_dice[0]
    assert rule.source_id == "dark-ones-own-luck"
    assert rule.dice_size == 10
    assert rule.test_kinds == ["saving_throw", "ability_check"]

    package = build_warlock_2014_spell_package(6)
    assert package.spells[-1].id == "dispel-magic"


def test_dark_ones_own_luck_can_rescue_a_failed_saving_throw() -> None:
    varek = build_combatant_state(build_varek_ashenmark_2014(6))
    before = next(item for item in varek.resources if item.id == "dark-ones-own-luck")
    assert before.current_uses == 1

    roll, succeeded = resolve_saving_throw(
        varek,
        "wisdom",
        15,
        FixedDiceProvider([5, 10]),
        round_number=1,
    )

    assert roll is not None
    assert succeeded is True
    assert "Dark One's Own Luck" in roll.notation
    assert next(item for item in varek.resources if item.id == "dark-ones-own-luck").current_uses == 0



def test_varek_levels_seven_and_eight_scale_existing_blaster_package() -> None:
    from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package

    l7 = build_varek_ashenmark_2014(7)
    l8 = build_varek_ashenmark_2014(8)
    p8 = build_varek_ashenmark_2014_profile(8)

    assert {item.id: item.max_uses for item in l7.resources if item.id.startswith("spell-slot-")} == {"spell-slot-4": 2}
    rays = next(item for item in l7.spell_attack_actions if item.id == "scorching-ray")
    assert rays.attack_count_at_slot(4) == 5

    assert p8.final_ability_scores.charisma == 20
    assert [(item.ability, item.amount) for item in p8.advancement_increases] == [
        ("charisma", 2), ("charisma", 2),
    ]
    blast = next(item for item in l8.spell_attack_actions if item.id == "eldritch-blast")
    assert blast.attack_bonus == 8
    assert blast.damage_bonus == 5
    assert blast.attack_count == 2

    assert len(build_warlock_2014_spell_package(7).spells) == 8
    assert len(build_warlock_2014_spell_package(8).spells) == 9


def test_varek_level_nine_uses_fifth_level_pact_magic_and_flame_strike() -> None:
    from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package

    varek = build_varek_ashenmark_2014(9)
    profile = build_varek_ashenmark_2014_profile(9)
    package = build_warlock_2014_spell_package(9)

    assert {item.id: item.max_uses for item in varek.resources if item.id.startswith("spell-slot-")} == {
        "spell-slot-5": 2,
    }
    assert profile.final_ability_scores.charisma == 20
    assert package.spells[-1].id == "flame-strike"
    assert len(package.spells) == warlock_2014_level(9).spells_known == 10

    flame_strike = next(item for item in varek.spell_save_actions if item.id == "flame-strike")
    assert flame_strike.level == 5
    assert len(flame_strike.damage_components) == 2
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["flame-strike"].automated is True
    assert audits["whispers-of-the-grave"].combat_relevant is False


def test_varek_level_ten_selects_best_fiendish_resilience_and_respects_weapon_bypass() -> None:
    from app.combat.damage_defenses import adjusted_damage_amount
    from app.combat.selectable_damage_resistance import resolve_selectable_damage_resistance
    from app.domain.damage_sources import DamageSourceQualifier
    from app.domain.weapons_base import DamageType

    varek = _member(build_varek_ashenmark_2014(10), "varek", "heroes", 0)
    enemy = _member(_commoner_2014(), "enemy", "monsters", 5)
    setup = EncounterSetup(
        heroes=[varek], monsters=[enemy], hero_total_levels=10, monster_total_cr="0", ruleset="2014",
    )

    event = resolve_selectable_damage_resistance(1, varek, setup)
    assert event is not None
    assert event.feature_id == "fiendish-resilience"
    assert "bludgeoning resistance" in event.description
    assert varek.state.opening_buff_id == "fiendish-resilience"

    defense = varek.state.active_conditional_damage_defenses[0]
    assert defense.damage_types == [DamageType.BLUDGEONING]
    assert set(defense.forbidden_source_qualifiers) == {
        DamageSourceQualifier.MAGICAL,
        DamageSourceQualifier.SILVERED,
    }

    ordinary_weapon = {
        DamageSourceQualifier.ATTACK,
        DamageSourceQualifier.WEAPON,
        DamageSourceQualifier.MELEE,
    }
    magical_weapon = {*ordinary_weapon, DamageSourceQualifier.MAGICAL}
    silvered_weapon = {*ordinary_weapon, DamageSourceQualifier.SILVERED}

    assert adjusted_damage_amount(
        10, DamageType.BLUDGEONING, varek.state, source_qualifiers=ordinary_weapon,
    ) == 5
    assert adjusted_damage_amount(
        10, DamageType.BLUDGEONING, varek.state, source_qualifiers=magical_weapon,
    ) == 10
    assert adjusted_damage_amount(
        10, DamageType.BLUDGEONING, varek.state, source_qualifiers=silvered_weapon,
    ) == 10


def test_varek_level_ten_has_four_cantrips_and_fiendish_resilience_audit() -> None:
    from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package

    profile = build_varek_ashenmark_2014_profile(10)
    package = build_warlock_2014_spell_package(10)
    varek = build_varek_ashenmark_2014(10)

    assert len(package.cantrips) == warlock_2014_level(10).cantrips_known == 4
    assert package.cantrips[-1].id == "prestidigitation"
    assert len(package.spells) == warlock_2014_level(10).spells_known == 10
    assert {item.id: item.max_uses for item in varek.resources if item.id.startswith("spell-slot-")} == {
        "spell-slot-5": 2,
    }
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["fiendish-resilience"].automated is True
