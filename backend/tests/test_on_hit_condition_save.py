from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_goblin_warrior
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant
from app.domain.size import CreatureSize
from app.domain.weapons import OnHitConditionSave


def _attacker(effect: OnHitConditionSave):
    state = build_combatant_state(build_karnok_stoneward().model_copy(update={"combat_traits": []}, deep=True))
    attack = state.template.weapon_attack.model_copy(update={
        "id": f"save-to-{effect.condition_id}-test",
        "on_hit_condition_save": effect,
    }, deep=True)
    return state, attack


def _target(*, size: CreatureSize = CreatureSize.MEDIUM, immune: str | None = None, creature_type: str | None = None, save_ability: str = "strength"):
    source = build_goblin_warrior()
    bonuses = dict(source.saving_throw_bonuses); bonuses[save_ability] = 0
    updates = {
        "armor_class": 10, "max_hp": 40, "saving_throw_bonuses": bonuses, "size": size,
        "condition_immunities": [immune] if immune else [],
    }
    if creature_type is not None:
        updates["creature_type"] = creature_type
    return build_combatant_state(source.model_copy(update=updates, deep=True))


def _hit(target, values, effect: OnHitConditionSave):
    attacker, attack = _attacker(effect)
    return resolve_attack(1, 1, attacker, target, attack, 5, FixedDiceProvider(values), spend_action=False)


def _prone():
    return OnHitConditionSave(save_ability="strength", dc=13, condition_id="prone", max_target_size=CreatureSize.LARGE)


def test_failed_on_hit_save_applies_condition_and_records_audit_fields() -> None:
    target = _target()
    event = _hit(target, [15, 4, 4, 5], _prone())
    assert event.hit is True
    assert event.save_ability == "strength"
    assert event.save_dc == 13
    assert event.save_succeeded is False
    assert event.saving_throw_roll is not None and event.saving_throw_roll.total == 5
    assert "prone" in event.applied_condition_ids
    assert "prone" in target.active_effect_ids


def test_successful_on_hit_save_does_not_apply_condition() -> None:
    target = _target()
    event = _hit(target, [15, 4, 4, 18], _prone())
    assert event.save_succeeded is True
    assert "prone" not in target.active_effect_ids
    assert "prone" not in event.applied_condition_ids


def test_on_hit_save_skips_oversized_and_immune_targets() -> None:
    huge = _target(size=CreatureSize.HUGE)
    immune = _target(immune="prone")
    huge_event = _hit(huge, [15, 4, 4], _prone())
    immune_event = _hit(immune, [15, 4, 4], _prone())
    assert huge_event.save_dc is None and "prone" not in huge.active_effect_ids
    assert immune_event.save_dc is None and "prone" not in immune.active_effect_ids


def test_failed_on_hit_save_applies_poisoned_without_a_new_resolver() -> None:
    effect = OnHitConditionSave(save_ability="constitution", dc=12, condition_id="poisoned")
    target = _target(save_ability="constitution")
    event = _hit(target, [15, 4, 4, 4], effect)
    assert event.save_succeeded is False
    assert "poisoned" in event.applied_condition_ids
    assert "poisoned" in target.active_effect_ids
    assert "Greatsword" in event.description
    assert "Poisoned" in event.description


def test_failed_on_hit_save_applies_timed_paralysis_and_skips_excluded_kinds() -> None:
    effect = OnHitConditionSave(
        save_ability="constitution", dc=10, condition_id="paralyzed",
        duration_rounds=10, repeat_save_timing="target_turn_end",
        excluded_creature_types=["undead"], excluded_creature_subtypes=["elf"],
    )
    target = _target(save_ability="constitution")
    event = _hit(target, [15, 4, 4, 3], effect)
    assert event.save_succeeded is False
    assert "paralyzed" in event.applied_condition_ids
    assert "paralyzed" in target.active_effect_ids
    timed = next(item for item in target.timed_effects if item.effect_id == "paralyzed")
    assert timed.repeat_save_ability == "constitution"
    assert timed.repeat_save_dc == 10
    assert timed.repeat_save_timing == "target_turn_end"
    assert timed.expires_round == 11
    assert timed.source_effect_id == "Greatsword"
    undead = _target(save_ability="constitution", creature_type="undead")
    elf = _target(save_ability="constitution", creature_type="Humanoid (Elf)")
    assert _hit(undead, [15, 4, 4], effect).save_dc is None
    assert "paralyzed" not in undead.active_effect_ids
    assert _hit(elf, [15, 4, 4], effect).save_dc is None
    assert "paralyzed" not in elf.active_effect_ids


def test_compiled_ghoul_claws_use_printed_name_and_shared_paralysis_save() -> None:
    ghoul = next(item for item in load_monster_source_2014() if item.id == "ghoul")
    template = compile_combatant(adapt_basic_monster_2014(ghoul))
    claws = next(item for item in [template.weapon_attack, *template.alternate_weapon_attacks] if item.weapon.name == "Claws")
    assert claws.on_hit_condition_save is not None
    assert claws.on_hit_condition_save.condition_id == "paralyzed"
    assert claws.on_hit_condition_save.dc == 10
    attacker = build_combatant_state(template)
    target = _target(save_ability="constitution")
    event = resolve_attack(1, 1, attacker, target, claws, 5, FixedDiceProvider([15, 2, 2, 2]), spend_action=False)
    assert event.hit is True
    assert event.save_succeeded is False
    assert "paralyzed" in event.applied_condition_ids
    assert "HIT with Claws" in event.description
    assert "Paralyzed" in event.description


def test_petrified_is_terminal_regardless_of_source_name() -> None:
    effect = OnHitConditionSave(save_ability="constitution", dc=12, condition_id="petrified")
    target = _target(save_ability="constitution")
    event = _hit(target, [15, 4, 4, 1], effect)
    assert event.save_succeeded is False
    assert "petrified" in target.active_effect_ids
    assert target.is_dead is True
    assert target.is_alive is False
    assert target.current_hp == 0


def test_staged_restrained_to_petrified_uses_same_terminal_condition_rule() -> None:
    effect = OnHitConditionSave(
        save_ability="constitution",
        dc=12,
        condition_id="restrained",
        repeat_save_timing="target_turn_end",
        repeat_save_failure_condition_id="petrified",
    )
    target = _target(save_ability="constitution")
    first = _hit(target, [15, 4, 4, 1], effect)
    assert first.save_succeeded is False
    assert "restrained" in target.active_effect_ids
    assert target.is_dead is False

    member = EncounterCombatant(
        combatant_id="target",
        side="monsters",
        position_ft=5,
        state=target,
    )
    events, _ = resolve_target_condition_timing(
        2, 1, member, "target_turn_end", FixedDiceProvider([1])
    )
    assert events[0].save_succeeded is False
    assert "restrained" not in target.active_effect_ids
    assert "petrified" in target.active_effect_ids
    assert target.is_dead is True
    assert target.current_hp == 0
