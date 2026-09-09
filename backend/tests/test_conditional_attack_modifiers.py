from __future__ import annotations

from app.combat.conditional_attack_modifiers import (
    conditional_attack_advantage_sources,
    conditional_attack_disadvantage_sources,
)
from app.content.monster_attack_roll_modifier_source_audit import (
    parse_attack_roll_modifier,
    unsupported_conditional_attack_modifier,
)
from app.content.roster import build_arena_roster
from app.domain.models import CombatantState


def _monster(name: str):
    return next(monster for monster in build_arena_roster().monsters if monster.name == name)


def _state(template):
    return CombatantState(template=template, current_hp=template.max_hp)


def test_source_parser_accepts_only_reviewed_target_missing_hp_clause() -> None:
    modifier = parse_attack_roll_modifier("(with Advantage if the target doesn't have all its Hit Points)")
    assert modifier is not None
    assert modifier.trigger == "target_missing_hp"
    assert modifier.mode == "advantage"
    assert unsupported_conditional_attack_modifier(
        "Bite. Melee Attack Roll: +6 (with Advantage if the target doesn't have all its Hit Points), reach 5 ft. Hit: 4 Piercing damage."
    ) is False
    assert unsupported_conditional_attack_modifier(
        "Bite. Melee Attack Roll: +6 (with Advantage while an ally is within 5 ft.), reach 5 ft. Hit: 4 Piercing damage."
    ) is True


def test_target_missing_hp_advantage_tracks_runtime_hp_state() -> None:
    shark = _monster("Hunter Shark")
    target = _monster("Ogre")
    attacker_state = _state(shark)
    target_state = _state(target)
    attack = shark.weapon_attack

    assert conditional_attack_advantage_sources(attacker_state, target_state, attack) == 0
    assert conditional_attack_disadvantage_sources(attacker_state, target_state, attack) == 0

    target_state.current_hp -= 1
    assert conditional_attack_advantage_sources(attacker_state, target_state, attack) == 1
    assert conditional_attack_disadvantage_sources(attacker_state, target_state, attack) == 0
