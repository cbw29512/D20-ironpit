from __future__ import annotations

from app.combat.attack_hit_damage import resolve_attack_hit_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.certified_heroes import build_certified_hero_registry
from app.content.demo import build_goblin_warrior
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.models import DamageType, RollMode


def test_2024_open_hand_monk_level20_body_and_mind_progression() -> None:
    template = build_kael_stillwater_2024(20)
    profile = build_kael_stillwater_2024_profile(20)
    fingerprint = build_kael_2024_combat_profiles(20)[-1]

    assert template.level == profile.level == fingerprint.level == 20
    assert template.ability_scores is not None
    assert (template.ability_scores.dexterity, template.ability_scores.wisdom) == (25, 18)
    assert profile.final_ability_scores == template.ability_scores == fingerprint.abilities
    assert profile.ability_score_maximums["dexterity"] == 25
    assert profile.ability_score_maximums["wisdom"] == 25

    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (21, 163, 60, 13)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (21, 163, 60, 13)
    assert (template.weapon_attack.attack_bonus, template.weapon_attack.damage_bonus) == (13, 7)
    assert template.saving_throw_bonuses["dexterity"] == 13
    assert template.saving_throw_bonuses["wisdom"] == 10
    assert template.skill_bonuses["acrobatics"] == 13
    assert template.skill_bonuses["insight"] == 10
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 20

    stunning = template.progression_features.resource_backed_on_hit_save_rider
    assert stunning is not None
    assert stunning.save_dc == 18

    redirect = template.attack_damage_reduction_reaction
    assert redirect is not None
    assert redirect.zero_damage_redirect is not None
    assert redirect.zero_damage_redirect.save_dc == 18

    wholeness = next(item for item in template.healing_actions if item.id == "wholeness-of-body")
    assert (wholeness.dice_size, wholeness.healing_bonus) == (12, 4)

    audit = next(item for item in profile.feature_audits if item.feature_id == "body-and-mind")
    assert audit.combat_relevant is True
    assert audit.automated is True

    registry = build_certified_hero_registry()
    assert registry[("monk", 20, "canonical")] == ("Kael Stillwater", "kael-stillwater-l20")


def test_monk20_inherited_irresistible_offense_scales_with_current_dexterity() -> None:
    attacker = build_combatant_state(build_kael_stillwater_2024(20))
    target_template = build_goblin_warrior().model_copy(
        update={"max_hp": 500, "damage_resistances": [DamageType.BLUDGEONING]},
        deep=True,
    )
    target = build_combatant_state(target_template)
    target.current_hp = 500

    result = resolve_attack_hit_damage(
        attacker,
        target,
        attacker.template.weapon_attack,
        FixedDiceProvider([1, 1]),
        critical=True,
        attack_mode=RollMode.NORMAL,
        turn_key="1:kael-l20",
        bonus_damage=None,
        affected_states=[attacker, target],
        sneak_attack_ally_available=False,
        natural_roll=20,
    )

    assert result.damage_components[0].applied_total == result.damage_components[0].total
    boon = next(item for item in result.damage_components if item.source == "Boon of Irresistible Offense")
    assert boon.total == 25
    assert boon.applied_total == 25
    assert boon.damage_type == DamageType.BLUDGEONING
