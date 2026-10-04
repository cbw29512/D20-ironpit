from __future__ import annotations

from app.combat.attack_effect_resolution import resolve_attack_effects
from app.combat.dice import FixedDiceProvider
from app.combat.exile import EXILED_EFFECT_ID, removed_from_battlefield
from app.combat.post_hit_spell_policy import extra_smite_beats_divine, expected_post_hit_dice
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.content.paladin_2024_smites import build_paladin_2024_extra_smites
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


def _hit(hero: EncounterCombatant, enemy: EncounterCombatant, setup: EncounterSetup, dice) -> None:
    begin_turn(hero.state)
    hero.state.feature_last_turn_keys["savage-attacker"] = "1:aurelia"
    resolve_attack_effects(
        hero.state,
        enemy.state,
        hero.state.template.weapon_attack,
        dice,
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


def test_extra_smites_bind_at_printed_levels_and_compete_by_damage() -> None:
    options = {item.id: item for item in build_paladin_2024_extra_smites(19, 19)}
    assert set(options) == {
        "thunderous-smite",
        "shining-smite",
        "blinding-smite",
        "staggering-smite",
        "banishing-smite",
    }
    assert options["thunderous-smite"].damage_type == "thunder"
    assert options["shining-smite"].attacks_against_advantage is True
    assert options["blinding-smite"].failed_condition_id == "blinded"
    assert options["blinding-smite"].repeat_save_timing == "target_turn_end"
    assert options["staggering-smite"].failed_condition_id == "stunned"
    assert options["banishing-smite"].exile_if_hp_at_or_below == 50
    assert expected_post_hit_dice(options["banishing-smite"], 5) == 27.5
    aurelia = build_combatant_state(build_aurelia_brightshield_2024(19))
    begin_turn(aurelia)
    assert extra_smite_beats_divine(aurelia, aurelia.template.weapon_attack, "1:aurelia") is True


def test_thunderous_smite_applies_printed_prone_and_push_when_divine_is_unavailable() -> None:
    template = build_aurelia_brightshield_2024(4)
    template = template.model_copy(update={
        "progression_features": template.progression_features.model_copy(update={
            "resource_backed_post_hit_damage": None,
        }),
    })
    hero = _member(template, "aurelia", "heroes", 4, 7)
    enemy = _member(build_commoner().model_copy(update={"max_hp": 40}, deep=True), "enemy", "monsters", 5, 7)
    setup = _setup(hero, enemy)
    start = enemy.state.position.model_copy(deep=True)
    _hit(hero, enemy, setup, FixedDiceProvider([8, 6, 6, 1]))
    assert hero.state.bonus_action_available is False
    assert hero.state.feature_last_turn_keys["paid-post-hit-spell"] == "thunderous-smite"
    assert "prone" in enemy.state.active_effect_ids
    assert enemy.state.position is not None
    assert abs(enemy.state.position.x - start.x) + abs(enemy.state.position.y - start.y) >= 1


def test_blinding_smite_blinds_on_a_failed_constitution_save_when_divine_is_unavailable() -> None:
    template = build_aurelia_brightshield_2024(9)
    template = template.model_copy(update={
        "progression_features": template.progression_features.model_copy(update={
            "resource_backed_post_hit_damage": None,
            "post_hit_spell_options": [
                item for item in template.progression_features.post_hit_spell_options
                if item.id == "blinding-smite"
            ],
        }),
    })
    hero = _member(template, "aurelia", "heroes", 4, 7)
    enemy = _member(build_commoner().model_copy(update={"max_hp": 40}, deep=True), "enemy", "monsters", 5, 7)
    setup = _setup(hero, enemy)
    _hit(hero, enemy, setup, FixedDiceProvider([8, 8, 8, 8, 1]))
    assert hero.state.feature_last_turn_keys["paid-post-hit-spell"] == "blinding-smite"
    assert "blinded" in enemy.state.active_effect_ids
    timed = next(item for item in enemy.state.timed_effects if item.effect_id == "blinded")
    assert timed.repeat_save_ability == "constitution"
    assert timed.repeat_save_timing == "target_turn_end"
    assert hero.state.concentration is not None
    assert hero.state.concentration.effect_id == "blinding-smite"


def test_banishing_smite_exiles_a_creature_left_at_or_below_fifty_hp() -> None:
    hero = _member(build_aurelia_brightshield_2024(19), "aurelia", "heroes", 4, 7)
    enemy = _member(
        build_commoner().model_copy(update={"max_hp": 80}, deep=True),
        "enemy",
        "monsters",
        5,
        7,
    )
    setup = _setup(hero, enemy)
    _hit(hero, enemy, setup, FixedDiceProvider([4, 4, 6, 6, 6, 6, 6]))
    assert hero.state.feature_last_turn_keys["paid-post-hit-spell"] == "banishing-smite"
    assert 0 < enemy.state.current_hp <= 50
    assert EXILED_EFFECT_ID in enemy.state.active_effect_ids
    assert removed_from_battlefield(enemy.state) is True
    assert hero.state.concentration is not None
    assert hero.state.concentration.effect_id == "banishing-smite"
