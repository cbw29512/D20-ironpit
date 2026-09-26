from __future__ import annotations

from app.combat.area_weapon_attacks import choose_area_weapon_attack, resolve_area_weapon_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.ranger_2014_spell_package import build_ranger_2014_spell_package
from app.content.ranger_hunter_2014_runtime import build_rowan_ashtrail_2014
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.models import EncounterCombatant, EncounterSetup


class MaxDiceProvider:
    def roll(self, sides: int) -> int:
        return sides


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=y)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def test_level_eleven_volley_uses_one_action_for_separate_area_attacks() -> None:
    hero = _member(build_rowan_ashtrail_2014(11), "rowan", "heroes", 1, 6)
    target_base = build_rowan_ashtrail_2014(1).model_copy(
        update={"armor_class": 10, "max_hp": 100, "area_weapon_attack_actions": []},
    )
    monsters = [
        _member(target_base.model_copy(update={"id": f"target-{index}", "name": f"Target {index}"}),
                f"target-{index}", "monsters", x, y)
        for index, (x, y) in enumerate(((8, 5), (8, 6), (8, 7)), start=1)
    ]
    setup = EncounterSetup(
        heroes=[hero], monsters=monsters, hero_total_levels=11, monster_total_cr="0",
        ruleset="2014", map_definition=BattleMapDefinition(id="volley-test", width_squares=20, height_squares=12),
    )
    begin_turn(hero.state)

    choice = choose_area_weapon_attack(hero, setup)
    assert choice is not None
    assert choice.action.id == "volley"
    assert choice.attack.weapon.id == "longbow"
    assert set(choice.placement.target_ids) == {"target-1", "target-2", "target-3"}

    events, sequence = resolve_area_weapon_attack(1, 1, hero, setup, MaxDiceProvider(), choice)
    attacks = [event for event in events if event.event_type == "attack"]

    assert hero.state.action_available is False
    assert sequence == 4
    assert len(attacks) == 3
    assert {event.target_id for event in attacks} == {"target-1", "target-2", "target-3"}
    assert all(event.weapon_id == "longbow" for event in attacks)
    assert all(event.feature_id == "volley" for event in attacks)
    assert all(event.attack_roll is not None for event in attacks)


def test_level_eleven_progression_and_known_spell_count_are_legal() -> None:
    hero = build_rowan_ashtrail_2014(11)
    package = build_ranger_2014_spell_package(11)

    assert hero.level == 11
    assert hero.max_hp == 92
    assert len(hero.area_weapon_attack_actions) == 1
    assert hero.area_weapon_attack_actions[0].area.radius_ft == 10
    assert {resource.id: resource.max_uses for resource in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
    }
    assert len(package.spells) == 7
    assert package.spells[-1].id == "water-walk"
