"""Pinned 2014 Beard source is a shared on-hit condition and healing restriction."""

from app.combat.attacks import resolve_attack
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.zero_hp import restore_hit_points
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant


def _attack_from_pinned_source():
    source = next(monster for monster in load_monster_source_2014()
                  if monster.id == "bearded-devil")
    beard = next(attack for attack in source.attacks if attack.id == "beard")
    assert source.multiattack_slots == [["beard"], ["glaive"]]
    assert beard.on_hit_save_effect == {
        "save_ability": "constitution", "dc": 12,
        "condition_id": "poisoned", "duration_rounds": 10,
        "repeat_save_timing": "target_turn_end", "cannot_regain_hit_points": True,
    }
    return compile_attack(_attack(source, beard))


def _target():
    template = build_karnok_stoneward().model_copy(deep=True)
    template.saving_throw_bonuses["constitution"] = 0
    state = build_combatant_state(template)
    state.current_hp = max(1, state.current_hp - 14)
    return state


def test_beard_binds_source_attack_and_qualifier() -> None:
    beard = _attack_from_pinned_source()
    assert beard.weapon.name == "Beard"
    assert beard.attack_bonus == 5 and beard.weapon.reach_ft == 5
    assert (beard.weapon.dice_count, beard.weapon.dice_size,
            beard.damage_bonus) == (1, 8, 2)
    effect = beard.on_hit_condition_save
    assert effect is not None and effect.condition_id == "poisoned"
    assert effect.cannot_regain_hit_points
    assert effect.repeat_save_timing == "target_turn_end"
    assert effect.duration_rounds == 10


def test_beard_failed_save_blocks_healing_until_repeat_save_succeeds() -> None:
    target = _target()
    attacker = build_combatant_state(build_goblin_warrior())
    attack = _attack_from_pinned_source()
    before = target.current_hp
    hit = resolve_attack(1, 1, attacker, target, attack, 5,
                         FixedDiceProvider([18, 2, 1]), spend_action=False)
    assert hit.hit and hit.save_succeeded is False
    assert target.current_hp < before
    assert "poisoned" in target.active_effect_ids
    owned = next(effect for effect in target.timed_effects
                 if effect.source_effect_id == "Beard")
    assert owned.cannot_regain_hit_points
    assert owned.repeat_save_dc == 12 and owned.repeat_save_ability == "constitution"
    assert owned.expires_round == 11
    assert restore_hit_points(target, 9) == 0
    member = EncounterCombatant(combatant_id="target", side="heroes",
                                position_ft=5, state=target)
    events, _ = resolve_target_condition_timing(
        2, 2, member, "target_turn_end", FixedDiceProvider([20])
    )
    assert events[0].save_succeeded is True
    assert "poisoned" not in target.active_effect_ids
    assert not target.timed_effects
    assert restore_hit_points(target, 9) > 0


def test_beard_poison_immunity_prevents_associated_heal_block() -> None:
    target = _target()
    target.template.condition_immunities.append("poisoned")
    attacker = build_combatant_state(build_goblin_warrior())
    hit = resolve_attack(1, 1, attacker, target, _attack_from_pinned_source(), 5,
                         FixedDiceProvider([18, 2]), spend_action=False)
    assert hit.hit and hit.save_dc is None
    assert not target.timed_effects
    assert restore_hit_points(target, 2) > 0
