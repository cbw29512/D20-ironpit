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


def _resistant_target():
    template = build_goblin_warrior().model_copy(
        update={"max_hp": 500, "damage_resistances": [DamageType.BLUDGEONING]},
        deep=True,
    )
    state = build_combatant_state(template)
    state.current_hp = 500
    return state


def _hit(natural_roll: int):
    attacker = build_combatant_state(build_kael_stillwater_2024(19))
    target = _resistant_target()
    result = resolve_attack_hit_damage(
        attacker,
        target,
        attacker.template.weapon_attack,
        FixedDiceProvider([1, 1]),
        critical=natural_roll == 20,
        attack_mode=RollMode.NORMAL,
        turn_key="1:kael-l19",
        bonus_damage=None,
        affected_states=[attacker, target],
        sneak_attack_ally_available=False,
        natural_roll=natural_roll,
    )
    return attacker, result


def test_2024_open_hand_monk_level19_binds_irresistible_offense() -> None:
    template = build_kael_stillwater_2024(19)
    profile = build_kael_stillwater_2024_profile(19)
    fingerprint = build_kael_2024_combat_profiles(19)[-1]
    features = template.progression_features

    assert template.level == profile.level == fingerprint.level == 19
    assert template.ability_scores is not None
    assert template.ability_scores.dexterity == 21
    assert profile.ability_score_maximums["dexterity"] == 30
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (17, 155, 60, 11)
    assert (fingerprint.armor_class, fingerprint.max_hp, fingerprint.speed_ft, fingerprint.initiative_bonus) == (17, 155, 60, 11)
    assert {item.id: item.max_uses for item in template.resources}["focus-points"] == 19
    assert [item.source_id for item in features.damage_resistance_bypass_grants] == ["boon-irresistible-offense"]
    assert set(features.damage_resistance_bypass_grants[0].damage_types) == {
        DamageType.BLUDGEONING,
        DamageType.PIERCING,
        DamageType.SLASHING,
    }
    assert [
        (item.source_id, item.ability, item.damage_type_source)
        for item in features.natural_twenty_attack_damage_grants
    ] == [("boon-irresistible-offense", "dexterity", "attack")]
    assert registry := build_certified_hero_registry()
    assert registry[("monk", 19, "canonical")] == ("Kael Stillwater", "kael-stillwater-l19")


def test_monk19_irresistible_offense_bypasses_resistance_and_adds_dexterity_score_on_20() -> None:
    _, result = _hit(20)

    assert len(result.damage_components) == 2
    base, boon = result.damage_components
    assert base.damage_type == DamageType.BLUDGEONING
    assert base.applied_total == base.total
    assert boon.source == "Boon of Irresistible Offense"
    assert boon.damage_type == DamageType.BLUDGEONING
    assert boon.total == 21
    assert boon.applied_total == 21


def test_monk19_overwhelming_strike_requires_natural_20() -> None:
    _, result = _hit(19)

    assert len(result.damage_components) == 1
    assert result.damage_components[0].applied_total == result.damage_components[0].total
