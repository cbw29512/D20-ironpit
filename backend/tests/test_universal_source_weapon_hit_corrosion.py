"""Verified post-hit weapon corrosion uses declarative equipment evidence."""
from __future__ import annotations

from app.combat.attack_effect_resolution import resolve_attack_effects
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.weapon_hit_corrosion import resolve_weapon_hit_corrosion
from app.content.demo import build_demo_fighter
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_weapon_corrosion_2014 import source_weapon_hit_corrosion_rule_2014
from app.domain.models import RollMode
from app.domain.weapon_hit_corrosion import WeaponHitCorrosionRule
from scripts.browser_template_serializer import template_row


def _rule():
    source = next(row for row in load_monster_source_2014() if row.id == "gray-ooze")
    rule = source_weapon_hit_corrosion_rule_2014(source)
    assert rule == WeaponHitCorrosionRule(source_name="Corrode Metal",
                                         qualifying_materials=["metal"])
    return rule


def _states_and_attack(material="metal", magical=False, ranged=False):
    source = build_demo_fighter()
    attacker = build_combatant_state(source)
    defender = build_combatant_state(source.model_copy(update={
        "weapon_hit_corrosion": _rule(),
    }))
    old_weapon = source.weapon_attack.weapon
    weapon = old_weapon.model_copy(update={
        "material": material, "is_magical": magical,
        **({"attack_kind": "ranged"} if ranged else {}),
    })
    attack = source.weapon_attack.model_copy(update={"weapon": weapon})
    return source, attacker, defender, attack


def test_corrosion_after_real_universal_hit_damage_and_browser_source_serialization():
    source, attacker, defender, attack = _states_and_attack()
    card_before = source.model_dump_json()
    result = resolve_attack_effects(
        attacker, defender, attack, FixedDiceProvider([4]),
        hit=True, critical=False, mode=RollMode.NORMAL, round_number=1,
        attacker_event_id="source", defender_event_id="target",
        actual_event_id="target", turn_key="1:source",
        bonus_damage=None, affected_states=[attacker, defender],
        sneak_attack_ally_available=False, brutal_strike_disadvantage=0,
    )
    assert result.damage_roll is not None and result.damage_roll.total > 0
    assert attacker.weapon_corrosion_penalties == {attack.weapon.id: 1}
    row = template_row(defender.template)
    assert row["weaponHitCorrosion"]["qualifyingMaterials"] == ["metal"]
    weapon_row = template_row(source.model_copy(update={
        "weapon_attack": attack
    }))["attacks"][0]
    assert weapon_row["weaponMaterial"] == "metal"
    assert weapon_row["weaponMagical"] is False
    assert source.model_dump_json() == card_before


def test_nonqualifying_or_unproven_weapons_are_unchanged():
    for material, magic, ranged in (
        (None, None, False), ("metal", None, False), (None, False, False),
        ("wood", False, False), ("other", False, False),
        ("metal", True, False), ("metal", False, True),
    ):
        _, attacker, defender, attack = _states_and_attack(material, magic, ranged)
        assert resolve_weapon_hit_corrosion(attacker, defender, attack) is None
        assert attacker.weapon_corrosion_penalties == {}


def test_each_weapon_is_independent_and_fifth_stack_is_unusable():
    _, attacker, defender, attack = _states_and_attack()
    for n in range(1, 6):
        assert resolve_weapon_hit_corrosion(attacker, defender, attack) == -n
    assert attacker.weapon_corrosion_penalties[attack.weapon.id] == 5
    assert attacker.weapon_corrosion_penalties.get("another-weapon", 0) == 0
    assert build_combatant_state(attacker.template).weapon_corrosion_penalties == {}
