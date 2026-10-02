from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import attacks_against_advantage_sources, effective_speed
from app.combat.resource_backed_on_hit_save import resolve_resource_backed_on_hit_save
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup() -> tuple[EncounterCombatant, EncounterCombatant, EncounterSetup]:
    monk = EncounterCombatant(
        combatant_id="hero-1:kael-stillwater-l5",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(build_kael_stillwater_2024(5)),
    )
    target_template = build_goblin_warrior().model_copy(
        update={"saving_throw_bonuses": {"constitution": 0}, "speed_ft": 30}
    )
    target = EncounterCombatant(
        combatant_id="monster-1:test-goblin",
        side="monsters",
        position_ft=10,
        state=build_combatant_state(target_template),
    )
    return monk, target, EncounterSetup(
        heroes=[monk],
        monsters=[target],
        hero_total_levels=5,
        monster_total_cr="0",
    )


def test_2024_monk_level_five_snapshot_extra_attack_and_fingerprint() -> None:
    try:
        profile = build_kael_stillwater_2024_profile(5)
        monk = build_kael_stillwater_2024(5)
        row = build_kael_2024_combat_profiles(5)[-1]
        resources = {item.id: item.max_uses for item in monk.resources}

        assert profile.final_ability_scores is not None
        assert profile.final_ability_scores.dexterity == 19
        assert monk.max_hp == 38
        assert monk.armor_class == 14
        assert monk.speed_ft == 40
        assert monk.initiative_bonus == 7
        assert monk.weapon_attack.attack_bonus == 7
        assert monk.weapon_attack.damage_bonus == 4
        assert monk.weapon_attack.weapon.dice_size == 8
        assert monk.progression_features.martial_arts_die_size == 8
        assert resources == {"focus-points": 5, "uncanny-metabolism": 1}
        assert monk.attack_action is not None
        assert monk.attack_action.is_attack_action is True
        assert [slot.attack_ids for slot in monk.attack_action.slots] == [
            ["kael-2024-unarmed"],
            ["kael-2024-unarmed"],
        ]

        rider = monk.progression_features.resource_backed_on_hit_save_rider
        assert rider is not None
        assert rider.source_id == "stunning-strike"
        assert rider.save_ability == "constitution"
        assert rider.save_dc == 11
        assert rider.once_per_turn is True
        assert rider.failed_condition_id == "stunned"
        assert rider.failed_condition_expiry_timing == "source_turn_start"
        assert rider.successful_save_speed_multiplier == 0.5
        assert rider.successful_save_next_attack_advantage is True

        assert row.level == 5
        assert row.initiative_bonus == 7
        assert row.attacks[0].dice_size == 8
        assert row.resources == (("focus-points", 5), ("uncanny-metabolism", 1))
    except Exception as exc:
        raise RuntimeError("2024 Monk level 5 snapshot certification failed.") from exc


def test_2024_stunning_strike_failed_save_is_once_per_turn_and_stuns() -> None:
    try:
        monk, target, setup = _setup()
        attack = monk.state.template.weapon_attack
        result = resolve_resource_backed_on_hit_save(
            1,
            1,
            monk,
            target,
            attack,
            FixedDiceProvider([1]),
            "1:hero-1:kael-stillwater-l5",
            affected_states=[monk.state, target.state],
            setup=setup,
        )

        assert result is not None
        assert result.event.feature_id == "stunning-strike"
        assert result.event.save_succeeded is False
        assert result.event.applied_condition_ids == ["stunned"]
        assert "stunned" in target.state.active_effect_ids
        timed = next(effect for effect in target.state.timed_effects if effect.effect_id == "stunned")
        assert timed.expiry_timing == "source_turn_start"
        focus = next(item for item in monk.state.resources if item.id == "focus-points")
        assert focus.current_uses == 4

        second = resolve_resource_backed_on_hit_save(
            2,
            1,
            monk,
            target,
            attack,
            FixedDiceProvider([1]),
            "1:hero-1:kael-stillwater-l5",
            affected_states=[monk.state, target.state],
            setup=setup,
        )
        assert second is None
        assert focus.current_uses == 4
    except Exception as exc:
        raise RuntimeError("2024 Stunning Strike failed-save/once-per-turn regression failed.") from exc


def test_2024_stunning_strike_success_halves_speed_and_grants_one_attack_advantage() -> None:
    try:
        monk, target, setup = _setup()
        attack = monk.state.template.weapon_attack
        result = resolve_resource_backed_on_hit_save(
            1,
            1,
            monk,
            target,
            attack,
            FixedDiceProvider([20]),
            "1:hero-1:kael-stillwater-l5",
            affected_states=[monk.state, target.state],
            setup=setup,
        )

        assert result is not None
        assert result.event.save_succeeded is True
        assert "stunned" not in target.state.active_effect_ids
        assert effective_speed(target.state) == 15
        assert attacks_against_advantage_sources(target.state) == 1
        advantage = next(
            item for item in target.state.active_modifiers
            if item.source_effect_id == "stunning-strike"
            and item.kind.value == "attacks-against-advantage"
        )
        speed = next(
            item for item in target.state.active_modifiers
            if item.source_effect_id == "stunning-strike"
            and item.kind.value == "speed-multiplier"
        )
        assert advantage.consume_on_attack_against is True
        assert advantage.expires_at_start_of_source_turn is True
        assert speed.multiplier == 0.5
        assert speed.expires_at_start_of_source_turn is True
    except Exception as exc:
        raise RuntimeError("2024 Stunning Strike success-rider regression failed.") from exc
