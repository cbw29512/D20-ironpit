from __future__ import annotations

from app.combat.attack_damage_reduction import apply_attack_damage_reduction
from app.combat.bonus_attacks import resolve_bonus_attack_grant
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageRollComponent, DamageType


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    try:
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=position,
            state=build_combatant_state(template),
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to build level-3 Monk test member {combatant_id}.") from exc


def _component(damage_type: DamageType, total: int) -> DamageRollComponent:
    try:
        return DamageRollComponent(
            source="test-hit",
            notation=str(total),
            rolls=[],
            modifier=total,
            damage_type=damage_type,
            total=total,
        )
    except Exception as exc:
        raise RuntimeError("Failed to build level-3 Monk test damage component.") from exc


def test_2024_monk_level_three_profile_and_runtime_are_raw_aligned() -> None:
    try:
        profile = build_kael_stillwater_2024_profile(3)
        monk = build_kael_stillwater_2024(3)

        assert profile.level == monk.level == 3
        assert profile.subclass_id == "warrior-of-the-open-hand"
        assert profile.subclass_name == "Warrior of the Open Hand"
        assert {"deflect-attacks", "open-hand-technique"}.issubset(
            {item.feature_id for item in profile.feature_audits}
        )
        assert monk.max_hp == 24
        assert monk.armor_class == 13
        assert monk.speed_ft == 40
        assert {item.id: item.max_uses for item in monk.resources} == {
            "focus-points": 3,
            "uncanny-metabolism": 1,
        }

        reaction = monk.attack_damage_reduction_reaction
        assert reaction is not None
        assert reaction.source_id == "deflect-attacks"
        assert reaction.source_name == "Deflect Attacks"
        assert set(reaction.attack_kinds) == {"melee", "ranged"}
        assert set(reaction.required_damage_types) == {
            DamageType.BLUDGEONING,
            DamageType.PIERCING,
            DamageType.SLASHING,
        }
        assert reaction.reduction_dice_count == 1
        assert reaction.reduction_dice_size == 10
        assert reaction.reduction_ability == "dexterity"
        assert reaction.add_level is True

        flurry = next(item for item in monk.bonus_attack_grants if item.id == "flurry-of-blows")
        martial = next(item for item in monk.bonus_attack_grants if item.id == "martial-arts")
        assert flurry.on_hit_condition_save is not None
        assert flurry.on_hit_condition_save.save_ability == "dexterity"
        assert flurry.on_hit_condition_save.dc == 10
        assert flurry.on_hit_condition_save.condition_id == "prone"
        assert martial.on_hit_condition_save is None
    except Exception as exc:
        raise RuntimeError("2024 Monk level 3 profile/runtime certification failed.") from exc


def test_2024_deflect_attacks_reduces_qualifying_melee_damage_and_spends_reaction() -> None:
    try:
        monk = build_combatant_state(build_kael_stillwater_2024(3))
        result = apply_attack_damage_reduction(
            monk,
            monk.template.weapon_attack,
            [_component(DamageType.BLUDGEONING, 12)],
            FixedDiceProvider([4]),
        )

        assert result.used is True
        assert result.source_id == "deflect-attacks"
        assert result.source_name == "Deflect Attacks"
        assert result.reduction == 10
        assert result.components[0].total == 2
        assert monk.reaction_available is False
    except Exception as exc:
        raise RuntimeError("2024 Deflect Attacks qualifying-hit regression failed.") from exc


def test_2024_deflect_attacks_ignores_attack_damage_without_bps_component() -> None:
    try:
        monk = build_combatant_state(build_kael_stillwater_2024(3))
        fire_attack = monk.template.weapon_attack.model_copy(
            update={
                "weapon": monk.template.weapon_attack.weapon.model_copy(
                    update={"damage_type": DamageType.FIRE}
                )
            }
        )
        result = apply_attack_damage_reduction(
            monk,
            fire_attack,
            [_component(DamageType.FIRE, 12)],
            FixedDiceProvider([1]),
        )

        assert result.used is False
        assert result.components[0].total == 12
        assert monk.reaction_available is True
    except Exception as exc:
        raise RuntimeError("2024 Deflect Attacks damage-type regression failed.") from exc


def test_2014_deflect_missiles_reuses_universal_reducer_but_remains_ranged_only() -> None:
    try:
        legacy = build_combatant_state(build_kael_stillwater_2014(3))
        rule = legacy.template.attack_damage_reduction_reaction
        assert rule is not None
        assert rule.source_id == "deflect-missiles"
        assert rule.attack_kinds == ["ranged"]

        melee = apply_attack_damage_reduction(
            legacy,
            legacy.template.weapon_attack,
            [_component(DamageType.BLUDGEONING, 8)],
            FixedDiceProvider([1]),
        )
        assert melee.used is False
        assert legacy.reaction_available is True
    except Exception as exc:
        raise RuntimeError("2014 Deflect Missiles edition-isolation regression failed.") from exc


def test_2024_open_hand_topple_is_composed_only_into_flurry_hits() -> None:
    try:
        monk = _member(build_kael_stillwater_2024(3), "monk", "heroes", 0)
        target_template = build_karnok_stoneward_level(1).model_copy(
            update={"armor_class": 1, "max_hp": 100}
        )
        target = _member(target_template, "target", "monsters", 5)
        # Isolate Open Hand's save rider from the Human Resourceful reroll on this borrowed target template.
        target.state.heroic_inspiration = False
        setup = EncounterSetup(
            heroes=[monk],
            monsters=[target],
            hero_total_levels=3,
            monster_total_cr="1",
            ruleset="2024",
        )

        events, sequence = resolve_bonus_attack_grant(
            1,
            1,
            monk,
            setup,
            FixedDiceProvider([10, 4, 1, 10, 4, 1]),
            "1:monk",
        )

        attacks = [event for event in events if event.event_type == "attack"]
        assert sequence >= 3
        assert len(attacks) == 2
        assert all(event.feature_id == "flurry-of-blows" for event in attacks)
        assert attacks[0].save_ability == "dexterity"
        assert attacks[0].save_dc == 10
        assert attacks[0].save_succeeded is False
        assert "prone" in target.state.active_effect_ids
        focus = next(item for item in monk.state.resources if item.id == "focus-points")
        assert focus.current_uses == 2

        fresh = _member(build_kael_stillwater_2024(3), "fresh", "heroes", 0)
        fresh_focus = next(item for item in fresh.state.resources if item.id == "focus-points")
        fresh_focus.current_uses = 0
        fresh_target = _member(target_template, "fresh-target", "monsters", 5)
        fresh_setup = EncounterSetup(
            heroes=[fresh],
            monsters=[fresh_target],
            hero_total_levels=3,
            monster_total_cr="1",
            ruleset="2024",
        )
        normal_events, _ = resolve_bonus_attack_grant(
            1,
            1,
            fresh,
            fresh_setup,
            FixedDiceProvider([10, 4]),
            "1:fresh",
        )
        normal_attack = next(event for event in normal_events if event.event_type == "attack")
        assert normal_attack.feature_id == "martial-arts"
        assert normal_attack.saving_throw_roll is None
        assert "prone" not in fresh_target.state.active_effect_ids
    except Exception as exc:
        raise RuntimeError("2024 Open Hand Technique Flurry composition regression failed.") from exc
