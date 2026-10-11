"""2014 Glaive / Infernal Wound via source-owned reusable HP-loss primitives."""

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.healing import resolve_healing
from app.combat.hit_point_loss import lose_hit_points
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant
from app.domain.models import HealingAction


def _source_glaive():
    monster = next(row for row in load_monster_source_2014()
                   if row.id == "bearded-devil")
    source = next(action for action in monster.attacks if action.id == "glaive")
    attack = compile_attack(_attack(monster, source))
    assert attack.weapon.name == "Glaive"
    assert attack.attack_bonus == 5 and attack.weapon.reach_ft == 10
    assert attack.on_hit_ongoing_hp_loss is not None
    assert attack.on_hit_ongoing_hp_loss.dc == 12
    assert attack.on_hit_ongoing_hp_loss.dice_count == 1
    assert attack.on_hit_ongoing_hp_loss.dice_size == 10
    return attack


def _target():
    template = build_karnok_stoneward().model_copy(deep=True)
    template.saving_throw_bonuses["constitution"] = 0
    template.max_hp = 100
    state = build_combatant_state(template)
    state.current_hp = 70
    return state


def test_glaive_failed_save_adds_one_source_owned_wound_and_stacks_without_save():
    attacker = build_combatant_state(build_karnok_stoneward())
    target = _target()
    glaive = _source_glaive()
    first = resolve_attack(1, 1, attacker, target, glaive, 10,
                           FixedDiceProvider([18, 3, 1]), actor_event_id="devil-1",
                           spend_action=False)
    assert first.hit and first.save_succeeded is False
    wound = next(effect for effect in target.timed_effects
                 if effect.effect_id == "infernal-wound")
    assert wound.source_id == "devil-1"
    assert wound.start_of_turn_hp_loss_dice_count == 1
    assert wound.ends_on_magical_healing and wound.expires_round is None
    second = resolve_attack(2, 1, attacker, target, glaive, 10,
                            FixedDiceProvider([18, 3]), actor_event_id="devil-1",
                            spend_action=False)
    assert second.hit
    assert wound.start_of_turn_hp_loss_dice_count == 2
    assert len(target.timed_effects) == 1
    target.temporary_hp = 30
    before = target.current_hp
    assert lose_hit_points(target, 7) == 7
    assert target.current_hp == before - 7
    assert target.temporary_hp == 30


def test_glaive_immunity_by_creature_type_and_successful_save():
    attacker = build_combatant_state(build_karnok_stoneward())
    glaive = _source_glaive()
    for kind in ("undead", "construct"):
        target = _target()
        target.template.creature_type = kind
        hit = resolve_attack(1, 1, attacker, target, glaive, 10,
                             FixedDiceProvider([18, 3]), spend_action=False)
        assert hit.hit and not target.timed_effects
    target = _target()
    hit = resolve_attack(1, 1, attacker, target, glaive, 10,
                         FixedDiceProvider([18, 3, 20]), spend_action=False)
    assert hit.hit and hit.save_succeeded is True
    assert not target.timed_effects


def test_wounds_from_different_devils_are_independent_and_magic_heal_closes_them():
    attacker = build_combatant_state(build_karnok_stoneward())
    target = _target()
    glaive = _source_glaive()
    for number in (1, 2):
        resolve_attack(number, 1, attacker, target, glaive, 10,
                       FixedDiceProvider([18, 3, 1]),
                       actor_event_id=f"devil-{number}", spend_action=False)
    assert sorted(effect.source_id for effect in target.timed_effects) == ["devil-1", "devil-2"]
    apply_timed_condition(
        target, "poisoned", "devil-beard", source_effect_id="Beard",
        cannot_regain_hit_points=True, use_default_poison_recovery=False,
        expires_at_start_of_source_turn=False,
    )
    member = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=0, state=target,
    )
    before = target.current_hp
    action = HealingAction(
        id="magical-healing-test", name="Magic Healing", action_cost="action",
        target_mode="self", healing_bonus=9, magical_healing=True,
    )
    event = resolve_healing(4, 2, member, member, action, FixedDiceProvider([1]))
    assert event.hp_after == before  # Beard still prevents actual HP gain.
    assert "poisoned" in target.active_effect_ids
    assert all(effect.effect_id != "infernal-wound" for effect in target.timed_effects)
    assert len([effect for effect in target.timed_effects if effect.effect_id == "poisoned"]) == 1
