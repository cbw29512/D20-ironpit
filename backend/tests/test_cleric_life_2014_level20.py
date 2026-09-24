from app.combat.healing import resolve_healing
from app.combat.state import build_combatant_state
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.encounters import EncounterCombatant


class NoRollDice:
    def roll(self, sides: int) -> int:
        raise AssertionError(f"Level-20 Divine Intervention must not roll d{sides}.")


def _member(level: int, combatant_id: str, hp: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_seraphine_dawnshield_2014(level)),
    )
    member.state.current_hp = hp
    return member


def test_level_twenty_advances_level_nineteen_without_rebuilding_seraphine() -> None:
    level_nineteen = build_seraphine_dawnshield_2014_profile(19)
    level_twenty = build_seraphine_dawnshield_2014_profile(20)

    assert level_twenty.character_name == level_nineteen.character_name == "Seraphine Dawnshield"
    assert level_twenty.species_id == level_nineteen.species_id == "hill-dwarf"
    assert level_twenty.background_id == level_nineteen.background_id == "acolyte"
    assert level_twenty.subclass_id == level_nineteen.subclass_id == "life-domain"
    assert level_twenty.class_equipment == level_nineteen.class_equipment
    assert level_twenty.advancement_increases == level_nineteen.advancement_increases
    assert level_twenty.final_ability_scores == level_nineteen.final_ability_scores
    assert level_twenty.feature_audits[:-1] == level_nineteen.feature_audits
    assert level_twenty.feature_audits[-1].feature_id == "divine-intervention-improvement"
    assert level_twenty.feature_audits[-1].automated is True


def test_level_twenty_runtime_and_resources_are_raw_ready() -> None:
    hero = build_seraphine_dawnshield_2014(20)
    profile = build_seraphine_dawnshield_2014_profile(20)
    combat = build_seraphine_2014_combat_profile(20)

    assert hero.max_hp == 223
    assert hero.armor_class == 16
    assert hero.ability_scores is not None
    assert hero.ability_scores.strength == 15
    assert hero.ability_scores.constitution == 20
    assert hero.ability_scores.wisdom == 20
    assert hero.progression_features.turning_failure_destroy_max_cr == "4"
    assert hero.progression_features.outgoing_healing_dice_maximizer is not None

    warhammer = hero.weapon_attack
    assert warhammer.attack_bonus == 8
    assert warhammer.damage_bonus == 2

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 3,
        "spell-slot-6": 2,
        "spell-slot-7": 2,
        "spell-slot-8": 1,
        "spell-slot-9": 1,
        "channel-divinity": 3,
        "divine-intervention": 1,
    }

    intervention = next(item for item in hero.healing_actions if item.id == "divine-intervention")
    assert intervention.restore_to_effective_max is True
    assert intervention.percentile_success_max is None
    assert intervention.resource_id == "divine-intervention"

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_level_twenty_divine_intervention_succeeds_without_d100_roll() -> None:
    cleric = _member(20, "cleric", 100)
    ally = _member(19, "ally", 10)
    action = next(
        item for item in cleric.state.template.healing_actions
        if item.id == "divine-intervention"
    )

    event = resolve_healing(1, 1, cleric, ally, action, NoRollDice(), "1:cleric")

    assert event.event_type == "healing"
    assert event.feature_roll is None
    assert event.healing_roll is not None
    assert event.healing_roll.notation == "restore-to-effective-max"
    assert ally.state.current_hp == ally.state.template.max_hp
    assert event.resource_remaining == 0
    assert cleric.state.resources[-1].id == "divine-intervention"
    assert cleric.state.resources[-1].current_uses == 0


def test_level_twenty_spell_package_has_full_prepared_capacity() -> None:
    package = build_cleric_2014_spell_package(20, 5)

    assert len(package.cantrips) == 5
    assert len(package.spells) == 25
    assert package.spells[-1].id == "blade-barrier"
    assert package.casting_ability == "wisdom"
