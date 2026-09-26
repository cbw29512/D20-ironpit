from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.spell_choice import SpellChoice
from app.combat.spell_resolution import resolve_spell
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_level_three_resources_spells_and_metamagic_are_explicit() -> None:
    hero = build_nyra_emberveil_2014(3)
    profile = build_nyra_emberveil_2014_profile(3)
    package = build_sorcerer_2014_spell_package(3)

    assert hero.level == 3
    assert profile.level == 3
    assert hero.max_hp == 17
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 2,
        "sorcery-points": 3,
    }
    assert [item.id for item in package.spells] == [
        "burning-hands",
        "detect-magic",
        "comprehend-languages",
        "knock",
    ]
    assert [item.id for item in hero.spell_save_disadvantage_options] == ["heightened-spell"]

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["heightened-spell"].combat_relevant is True
    assert audits["heightened-spell"].automated is True
    assert audits["subtle-spell"].combat_relevant is False


def test_level_three_flexible_casting_includes_second_level_slot_exchanges() -> None:
    hero = build_nyra_emberveil_2014(3)
    actions = {item.id: item for item in hero.resource_conversion_actions}

    assert set(actions) == {
        "create-spell-slot-1",
        "convert-spell-slot-1",
        "create-spell-slot-2",
        "convert-spell-slot-2",
    }
    assert actions["create-spell-slot-2"].source_cost == 3
    assert actions["convert-spell-slot-2"].target_gain == 2


def test_heightened_spell_spends_points_and_uses_shared_disadvantage_save_mode() -> None:
    nyra = _member(build_nyra_emberveil_2014(3), "nyra", "heroes", 0)
    enemy_template = build_commoner().model_copy(update={
        "ruleset": "2014",
        "max_hp": 30,
        "saving_throw_bonuses": {
            "strength": 0,
            "dexterity": 0,
            "constitution": 0,
            "intelligence": 0,
            "wisdom": 0,
            "charisma": 0,
        },
    })
    enemy = _member(enemy_template, "enemy", "monsters", 10)
    setup = EncounterSetup(
        heroes=[nyra],
        monsters=[enemy],
        hero_total_levels=3,
        monster_total_cr="0",
        ruleset="2014",
    )
    spell = next(item for item in nyra.state.template.spell_save_actions if item.id == "burning-hands")
    choice = SpellChoice(spell, 1, (enemy.combatant_id,))

    events, _ = resolve_spell(
        1,
        1,
        nyra,
        setup,
        choice,
        "1:nyra",
        FixedDiceProvider([20, 1, 4, 4, 4]),
    )

    save_event = next(event for event in events if event.event_type == "saving_throw")
    points = next(item for item in nyra.state.resources if item.id == "sorcery-points")

    assert points.current_uses == 0
    assert save_event.resource_remaining == 0
    assert save_event.saving_throw_roll is not None
    assert save_event.saving_throw_roll.mode.value == "disadvantage"
    assert save_event.saving_throw_roll.rolls == [20, 1]
    assert save_event.save_succeeded is False
    assert "Heightened Spell imposes Disadvantage" in save_event.description
