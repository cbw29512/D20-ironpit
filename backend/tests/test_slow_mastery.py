from __future__ import annotations

from app.combat.modifier_stack import effective_speed
from app.combat.slow import apply_weapon_slow, weapon_slow_eligible
from app.combat.state import build_combatant_state
from app.content.ranger_hunter_2024_runtime import build_rowan_ashtrail_2024
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024


def test_longbow_slow_reduces_target_speed_until_source_turn() -> None:
    ranger = build_combatant_state(build_rowan_ashtrail_2024(1))
    target = build_combatant_state(build_rowan_ashtrail_2024(1))
    attack = ranger.template.weapon_attack
    assert attack.weapon.mastery_property == "Slow"
    assert weapon_slow_eligible(ranger, attack) is True
    before = effective_speed(target)
    assert apply_weapon_slow(ranger, "rowan", target, attack, 1) is True
    assert effective_speed(target) == max(0, before - 10)
    modifier = next(item for item in target.active_modifiers if item.source_effect_id == "weapon-mastery-slow")
    assert modifier.expires_at_start_of_source_turn is True
    assert modifier.flat_bonus == -10


def test_paladin_javelin_slow_uses_the_same_mastery() -> None:
    paladin = build_combatant_state(build_aurelia_brightshield_2024(1))
    target = build_combatant_state(build_rowan_ashtrail_2024(1))
    javelin = paladin.template.alternate_weapon_attacks[0]
    assert javelin.weapon.mastery_property == "Slow"
    assert apply_weapon_slow(paladin, "aurelia", target, javelin, 1) is True
    assert effective_speed(target) == target.template.speed_ft - 10


def test_unmastered_slow_weapon_does_not_apply() -> None:
    ranger = build_combatant_state(build_rowan_ashtrail_2024(1))
    target = build_combatant_state(build_rowan_ashtrail_2024(1))
    scimitar = ranger.template.alternate_weapon_attacks[1]
    assert scimitar.weapon.mastery_property is None
    assert apply_weapon_slow(ranger, "rowan", target, scimitar, 1) is False
    assert effective_speed(target) == target.template.speed_ft
