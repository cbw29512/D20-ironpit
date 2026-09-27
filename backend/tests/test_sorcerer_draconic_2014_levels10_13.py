from __future__ import annotations

from app.combat.spell_attack_policy import choose_spell_attack
from app.combat.spell_range_modifiers import (
    choose_spell_range_modifier,
    effective_spell_range_ft,
    spend_spell_range_modifier,
)
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _encounter(level: int, distance_ft: int) -> tuple[EncounterCombatant, EncounterSetup]:
    nyra = EncounterCombatant(
        combatant_id="nyra",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_nyra_emberveil_2014(level)),
    )
    enemy = EncounterCombatant(
        combatant_id="enemy",
        side="monsters",
        position_ft=distance_ft,
        state=build_combatant_state(build_commoner().model_copy(update={"ruleset": "2014", "max_hp": 20})),
    )
    return nyra, EncounterSetup(
        heroes=[nyra],
        monsters=[enemy],
        hero_total_levels=level,
        monster_total_cr="0",
        ruleset="2014",
    )


def test_level_ten_distant_spell_extends_only_when_needed() -> None:
    nyra, setup = _encounter(10, 200)
    fire_bolt = next(item for item in nyra.state.template.spell_attack_actions if item.id == "fire-bolt")

    assert fire_bolt.range_ft == 120
    assert effective_spell_range_ft(nyra.state, fire_bolt.range_ft) == 240

    option = choose_spell_range_modifier(
        nyra.state,
        base_range_ft=fire_bolt.range_ft,
        required_range_ft=200,
    )
    assert option is not None
    assert option.id == "distant-spell"
    assert option.resource_cost == 1

    choice = choose_spell_attack(nyra, setup, "1:nyra")
    assert choice is not None
    assert choice.action.id == "fire-bolt"
    assert choice.range_modifier is not None
    assert choice.range_modifier.id == "distant-spell"

    points = next(item for item in nyra.state.resources if item.id == "sorcery-points")
    assert points.current_uses == 10
    remaining = spend_spell_range_modifier(nyra.state, choice.range_modifier)
    assert remaining == 9
    assert points.current_uses == 9


def test_level_ten_distant_spell_is_not_spent_inside_normal_range() -> None:
    nyra, setup = _encounter(10, 100)
    choice = choose_spell_attack(nyra, setup, "1:nyra")

    assert choice is not None
    assert choice.action.id == "fire-bolt"
    assert choice.range_modifier is None


def test_levels_ten_through_thirteen_keep_persistent_progression() -> None:
    expected = {
        10: (20, 12, 62, 11, 6),
        11: (20, 12, 68, 12, 6),
        12: (20, 14, 86, 12, 6),
        13: (20, 14, 93, 13, 6),
    }
    for level, (charisma, constitution, hp, spells_known, cantrips_known) in expected.items():
        hero = build_nyra_emberveil_2014(level)
        profile = build_nyra_emberveil_2014_profile(level)
        package = build_sorcerer_2014_spell_package(level)

        assert profile.final_ability_scores.charisma == charisma
        assert profile.final_ability_scores.constitution == constitution
        assert hero.max_hp == hp
        assert len(package.spells) == spells_known
        assert len(package.cantrips) == cantrips_known
        assert next(item for item in hero.resources if item.id == "sorcery-points").max_uses == level


def test_level_thirteen_spell_slots_match_2014_progression() -> None:
    hero = build_nyra_emberveil_2014(13)
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "spell-slot-6": 1,
        "spell-slot-7": 1,
        "sorcery-points": 13,
    }
