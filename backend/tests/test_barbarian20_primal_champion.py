from __future__ import annotations

from app.combat.attack_hit_damage import resolve_attack_hit_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.barbarian_level20_profile import build_rokhan_stonefury_level20_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.certified_heroes import build_certified_hero_registry
from app.content.demo import build_goblin_warrior
from app.domain.models import DamageType, RollMode


def test_level20_primal_champion_uses_normal_score_progression() -> None:
    profile = build_rokhan_stonefury_level20_profile()
    template = build_rokhan_stonefury_level(20)

    assert profile.level == 20
    assert profile.final_ability_scores.strength == 25
    assert profile.final_ability_scores.constitution == 24
    assert profile.ability_score_maximums["strength"] == 25
    assert profile.ability_score_maximums["constitution"] == 25

    assert template.ability_scores is not None
    assert template.ability_scores.strength == 25
    assert template.ability_scores.constitution == 24
    assert template.armor_class == 18
    assert template.max_hp == 285
    assert template.weapon_attack.attack_bonus == 13
    assert template.weapon_attack.damage_bonus == 7
    assert template.saving_throw_bonuses["strength"] == 13
    assert template.saving_throw_bonuses["constitution"] == 13
    assert template.skill_bonuses["athletics"] == 13
    assert ("barbarian", 20, "canonical") in build_certified_hero_registry()


def test_level20_inherited_indomitable_might_uses_strength_25_floor() -> None:
    template = build_rokhan_stonefury_level(20)

    assert [(item.source_id, item.ability) for item in template.progression_features.ability_check_minimums] == [
        ("indomitable-might", "strength"),
    ]
    assert [(item.source_id, item.ability) for item in template.progression_features.saving_throw_minimums] == [
        ("indomitable-might", "strength"),
    ]


def test_level20_inherited_irresistible_offense_scales_with_current_strength() -> None:
    attacker = build_combatant_state(build_rokhan_stonefury_level(20))
    target_template = build_goblin_warrior().model_copy(
        update={"max_hp": 500, "damage_resistances": [DamageType.SLASHING]},
        deep=True,
    )
    target = build_combatant_state(target_template)
    target.current_hp = 500

    result = resolve_attack_hit_damage(
        attacker,
        target,
        attacker.template.weapon_attack,
        FixedDiceProvider([1, 1, 10, 10]),
        critical=True,
        attack_mode=RollMode.NORMAL,
        turn_key="1:rokhan-l20",
        bonus_damage=None,
        affected_states=[attacker, target],
        sneak_attack_ally_available=False,
        natural_roll=20,
    )

    assert result.damage_components[0].applied_total == result.damage_components[0].total
    boon = next(item for item in result.damage_components if item.source == "Boon of Irresistible Offense")
    assert boon.total == 25
    assert boon.applied_total == 25
    assert boon.damage_type == DamageType.SLASHING
