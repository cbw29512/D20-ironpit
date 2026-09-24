from app.combat.dice import FixedDiceProvider
from app.combat.healing import choose_healing_action, resolve_healing
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(level: int, combatant_id: str, hp: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_seraphine_dawnshield_2014(level)),
    )
    member.state.current_hp = hp
    return member


def _setup(cleric: EncounterCombatant, ally: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[cleric, ally],
        monsters=[],
        hero_total_levels=cleric.state.template.level + ally.state.template.level,
        monster_total_cr="0",
        starting_distance_ft=0,
        ruleset="2014",
    )


def test_level_ten_advances_level_nine_without_rebuilding_seraphine() -> None:
    level_nine = build_seraphine_dawnshield_2014_profile(9)
    level_ten = build_seraphine_dawnshield_2014_profile(10)

    assert level_ten.character_name == level_nine.character_name == "Seraphine Dawnshield"
    assert level_ten.species_id == level_nine.species_id == "hill-dwarf"
    assert level_ten.background_id == level_nine.background_id == "acolyte"
    assert level_ten.subclass_id == level_nine.subclass_id == "life-domain"
    assert level_ten.class_equipment == level_nine.class_equipment
    assert level_ten.advancement_increases == level_nine.advancement_increases
    assert level_ten.final_ability_scores == level_nine.final_ability_scores
    assert level_ten.feature_audits[:-1] == level_nine.feature_audits
    assert level_ten.feature_audits[-1].feature_id == "divine-intervention"


def test_level_ten_runtime_binds_percentile_full_heal_and_resource() -> None:
    hero = build_seraphine_dawnshield_2014(10)
    profile = build_seraphine_dawnshield_2014_profile(10)
    combat = build_seraphine_2014_combat_profile(10)

    assert hero.max_hp == 93
    assert hero.ability_scores is not None and hero.ability_scores.wisdom == 20
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "channel-divinity": 2,
        "divine-intervention": 1,
    }

    action = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert action.name == "Divine Intervention"
    assert action.action_cost == "action"
    assert action.target_mode == "self_or_ally"
    assert action.restore_to_effective_max is True
    assert action.percentile_success_max == 10
    assert action.resource_id == "divine-intervention"

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_divine_intervention_targets_most_injured_bloodied_party_member() -> None:
    cleric = _member(10, "cleric", 60)
    ally = _member(9, "ally", 10)
    setup = _setup(cleric, ally)

    choice = choose_healing_action(cleric, setup, "1:cleric")
    assert choice is not None
    action, target = choice
    assert action.id == "divine-intervention"
    assert target.combatant_id == "ally"


def test_divine_intervention_failure_spends_attempt_and_heals_nothing() -> None:
    cleric = _member(10, "cleric", 60)
    ally = _member(9, "ally", 10)
    setup = _setup(cleric, ally)
    action, target = choose_healing_action(cleric, setup, "1:cleric")

    before = target.state.current_hp
    event = resolve_healing(
        1, 1, cleric, target, action, FixedDiceProvider([11]), "1:cleric",
    )

    assert event.event_type == "feature"
    assert event.feature_roll is not None and event.feature_roll.total == 11
    assert target.state.current_hp == before
    assert event.resource_remaining == 0
    assert cleric.state.resources[-1].id == "divine-intervention"
    assert cleric.state.resources[-1].current_uses == 0


def test_divine_intervention_success_restores_effective_max_hp() -> None:
    cleric = _member(10, "cleric", 60)
    ally = _member(9, "ally", 10)
    setup = _setup(cleric, ally)
    action, target = choose_healing_action(cleric, setup, "1:cleric")

    event = resolve_healing(
        1, 1, cleric, target, action, FixedDiceProvider([10]), "1:cleric",
    )

    assert event.event_type == "healing"
    assert event.feature_roll is not None and event.feature_roll.total == 10
    assert event.healing_roll is not None
    assert event.healing_roll.notation == "restore-to-effective-max"
    assert target.state.current_hp == target.state.template.max_hp
    assert event.hp_after == target.state.template.max_hp
    assert event.resource_remaining == 0
