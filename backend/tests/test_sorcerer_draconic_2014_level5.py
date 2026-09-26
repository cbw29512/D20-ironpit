from __future__ import annotations

from app.combat.spell_policy import choose_spell
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.sorcerer_2014_spell_package import build_sorcerer_2014_spell_package
from app.content.sorcerer_draconic_2014_profile import build_nyra_emberveil_2014_profile
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.models import EncounterCombatant, EncounterSetup


def test_level_five_progression_adds_third_level_slots_and_scaled_fire_bolt() -> None:
    hero = build_nyra_emberveil_2014(5)
    profile = build_nyra_emberveil_2014_profile(5)

    assert hero.level == 5
    assert profile.level == 5
    assert hero.max_hp == 27
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 2,
        "sorcery-points": 5,
    }

    fire_bolt = next(action for action in hero.spell_attack_actions if action.id == "fire-bolt")
    assert fire_bolt.attack_bonus == 7
    assert fire_bolt.damage_dice_count == 2
    assert fire_bolt.damage_dice_size == 10


def test_level_five_fireball_uses_shared_area_save_damage_shape() -> None:
    hero = build_nyra_emberveil_2014(5)
    fireball = next(action for action in hero.spell_save_actions if action.id == "fireball")

    assert fireball.level == 3
    assert fireball.action_cost == "action"
    assert fireball.range_ft == 150
    assert fireball.area is not None
    assert fireball.area.shape == "radius"
    assert fireball.area.origin == "point"
    assert fireball.area.radius_ft == 20
    assert fireball.save_ability == "dexterity"
    assert fireball.dc == 15
    assert fireball.damage_dice_count == 8
    assert fireball.damage_dice_size == 6
    assert fireball.damage_type == "fire"
    assert fireball.success_damage == "half"
    assert fireball.upcast_dice_per_level == 1


def test_level_five_spell_package_is_six_known_spells() -> None:
    package = build_sorcerer_2014_spell_package(5)

    assert len(package.cantrips) == 5
    assert [item.id for item in package.spells] == [
        "burning-hands",
        "detect-magic",
        "comprehend-languages",
        "knock",
        "detect-thoughts",
        "fireball",
    ]


def test_level_five_python_policy_selects_fireball_as_universal_area_spell() -> None:
    hero_state = build_combatant_state(build_nyra_emberveil_2014(5))
    hero_state.position = GridPosition(x=1, y=6)
    hero = EncounterCombatant(combatant_id="nyra", side="heroes", position_ft=5, state=hero_state)

    target_template = build_commoner().model_copy(update={"ruleset": "2014", "max_hp": 40})
    monsters = []
    for index, (x, y) in enumerate(((8, 5), (8, 6), (8, 7)), start=1):
        state = build_combatant_state(target_template.model_copy(
            update={"id": f"target-{index}", "name": f"Target {index}"},
        ))
        state.position = GridPosition(x=x, y=y)
        monsters.append(EncounterCombatant(
            combatant_id=f"target-{index}", side="monsters", position_ft=x * 5, state=state,
        ))

    setup = EncounterSetup(
        heroes=[hero],
        monsters=monsters,
        hero_total_levels=5,
        monster_total_cr="0",
        ruleset="2014",
        map_definition=BattleMapDefinition(id="fireball-policy", width_squares=20, height_squares=12),
    )

    choice = choose_spell(hero, setup, "1:nyra")
    assert choice is not None
    assert choice.action.id == "fireball"
    assert choice.placement is not None
    assert set(choice.target_ids) == {"target-1", "target-2", "target-3"}
