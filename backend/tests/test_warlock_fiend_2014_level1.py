from app.combat.dice import FixedDiceProvider
from app.combat.spell_attack_resolution import resolve_spell_attack
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
    assert [item.id for item in varek.spell_save_actions] == ["poison-spray", "burning-hands", "shatter"]

    package = build_warlock_2014_spell_package(3)
    assert [item.id for item in package.spells] == [
        "hex", "burning-hands", "comprehend-languages", "shatter",
    ]
