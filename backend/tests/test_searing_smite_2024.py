from __future__ import annotations

from app.combat.attack_effect_resolution import resolve_attack_effects
from app.combat.dice import FixedDiceProvider
from app.combat.start_of_turn_save_condition_events import (
    resolve_start_of_turn_save_condition_damage_events,
)
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import RollMode


def _member(template, combatant_id: str, side: str, x: int, y: int, *, max_hp: int | None = None) -> EncounterCombatant:
    built = template if max_hp is None else template.model_copy(update={"max_hp": max_hp}, deep=True)
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=abs(x) * 5,
        state=build_combatant_state(built),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def _setup(hero: EncounterCombatant, enemy: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[hero],
        monsters=[enemy],
        hero_total_levels=hero.state.template.level,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )


def test_searing_smite_deals_immediate_fire_and_start_of_turn_burn() -> None:
    template = build_aurelia_brightshield_2024(3)
    template = template.model_copy(update={
        "progression_features": template.progression_features.model_copy(update={
            "resource_backed_post_hit_damage": None,
            "post_hit_spell_options": [
                item for item in template.progression_features.post_hit_spell_options
                if item.id == "searing-smite"
            ],
        }),
    })
    hero = _member(template, "aurelia", "heroes", 4, 7)
    enemy = _member(build_commoner().model_copy(update={"max_hp": 40}, deep=True), "enemy", "monsters", 5, 7)
    setup = _setup(hero, enemy)
    begin_turn(hero.state)
    hero.state.feature_last_turn_keys["savage-attacker"] = "1:aurelia"
    before = enemy.state.current_hp
    resolve_attack_effects(
        hero.state,
        enemy.state,
        hero.state.template.weapon_attack,
        FixedDiceProvider([8, 6]),
        hit=True,
        critical=False,
        mode=RollMode.NORMAL,
        round_number=1,
        attacker_event_id=hero.combatant_id,
        defender_event_id=enemy.combatant_id,
        actual_event_id=enemy.combatant_id,
        turn_key="1:aurelia",
        bonus_damage=None,
        affected_states=[hero.state, enemy.state],
        sneak_attack_ally_available=False,
        brutal_strike_disadvantage=0,
        setup=setup,
    )
    assert hero.state.feature_last_turn_keys["paid-post-hit-spell"] == "searing-smite"
    assert enemy.state.current_hp == before - 8 - hero.state.template.weapon_attack.damage_bonus - 6
    burn = next(item for item in enemy.state.timed_effects if item.effect_id == "searing-smite")
    assert burn.start_of_turn_dice_count == 1
    assert burn.start_of_turn_damage_type is not None
    assert str(burn.start_of_turn_damage_type) == "fire"
    assert burn.start_of_turn_save_ends is True

    after_hit = enemy.state.current_hp
    resolve_start_of_turn_save_condition_damage_events(
        1, 2, enemy, setup, FixedDiceProvider([6, 1]),
    )
    assert enemy.state.current_hp == after_hit - 6
    assert any(item.effect_id == "searing-smite" for item in enemy.state.timed_effects)

    resolve_start_of_turn_save_condition_damage_events(
        2, 3, enemy, setup, FixedDiceProvider([4, 20]),
    )
    assert enemy.state.current_hp == after_hit - 6 - 4
    assert all(item.effect_id != "searing-smite" for item in enemy.state.timed_effects)
