"""2014 Glaive wound attack and generic direct-HP-loss interactions."""

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.healing import resolve_healing
from app.combat.state import build_combatant_state
from app.combat.start_of_turn_hp_loss import resolve_start_of_turn_hp_loss_events
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant
from app.domain.models import HealingAction
from app.domain.timed_effects import TimedEffect


def _glaive():
    monster = next(row for row in load_monster_source_2014()
                   if row.id == "bearded-devil")
    source = next(row for row in monster.attacks if row.id == "glaive")
    attack = compile_attack(_attack(monster, source))
    assert attack.weapon.name == "Glaive"
    assert attack.attack_bonus == 5
    assert attack.weapon.reach_ft == 10
    assert attack.on_hit_ongoing_hp_loss is not None
    assert attack.on_hit_ongoing_hp_loss.dc == 12
    assert attack.on_hit_ongoing_hp_loss.dice_size == 10
    return attack


def _target():
    template = build_karnok_stoneward().model_copy(deep=True)
    template.saving_throw_bonuses["constitution"] = 0
    template.max_hp = 100
    state = build_combatant_state(template)
    state.current_hp = 70
    return state


def test_infernal_wound_save_then_stacks_without_new_save():
    attacker = build_combatant_state(build_goblin_warrior())
    target = _target()
    glaive = _glaive()
    first = resolve_attack(
        1, 1, attacker, target, glaive, 10, FixedDiceProvider([18, 3, 1]),
        actor_event_id="devil-one", spend_action=False,
    )
    assert first.hit and first.save_succeeded is False
    wound = next(effect for effect in target.timed_effects
                 if effect.effect_id == "infernal-wound")
    assert wound.source_id == "devil-one"
    assert wound.source_effect_id == "Infernal Wound"
    assert wound.start_of_turn_hp_loss_dice_count == 1
    assert wound.ends_on_magical_healing and wound.expires_round is None
    second = resolve_attack(
        2, 1, attacker, target, glaive, 10, FixedDiceProvider([18, 3]),
        actor_event_id="devil-one", spend_action=False,
    )
    assert second.hit
    assert wound.start_of_turn_hp_loss_dice_count == 2
    assert len(target.timed_effects) == 1
    target.temporary_hp = 30
    member = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=0, state=target,
    )
    before = target.current_hp
    events, sequence = resolve_start_of_turn_hp_loss_events(
        1, 2, member, type("Setup", (), {"heroes": [member], "monsters": []})(),
        FixedDiceProvider([3, 4]),
    )
    assert sequence == 2 and len(events) == 1
    assert target.current_hp == before - 7
    assert target.temporary_hp == 30


def test_infernal_wound_excluded_types_and_successful_save():
    attacker = build_combatant_state(build_goblin_warrior())
    glaive = _glaive()
    for kind in ("undead", "construct"):
        target = _target()
        target.template.creature_type = kind
        result = resolve_attack(
            1, 1, attacker, target, glaive, 10, FixedDiceProvider([18, 3]),
            spend_action=False,
        )
        assert result.hit and not target.timed_effects
    target = _target()
    result = resolve_attack(
        1, 1, attacker, target, glaive, 10, FixedDiceProvider([18, 3, 20]),
        spend_action=False,
    )
    assert result.hit and result.save_succeeded is True
    assert not target.timed_effects


def test_infernal_wound_sources_independent_magic_heal_closes_both():
    attacker = build_combatant_state(build_goblin_warrior())
    target = _target()
    glaive = _glaive()
    for number in (1, 2):
        resolve_attack(
            number, 1, attacker, target, glaive, 10,
            FixedDiceProvider([18, 3, 1]), actor_event_id=f"devil-{number}",
            spend_action=False,
        )
    assert sorted(effect.source_id for effect in target.timed_effects) == [
        "devil-1", "devil-2",
    ]
    target.timed_effects.append(TimedEffect(
        effect_id="poisoned", source_id="beard", source_effect_id="Beard",
        cannot_regain_hit_points=True, expires_at_start_of_source_turn=False,
    ))
    target.active_effect_ids.append("poisoned")
    member = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=0, state=target,
    )
    before = target.current_hp
    action = HealingAction(
        id="magic-healing", name="Magical Healing", action_cost="action",
        target_mode="self", healing_bonus=9, magical_healing=True,
    )
    healed = resolve_healing(4, 2, member, member, action, FixedDiceProvider([1]))
    assert healed.hp_after == before
    assert not any(effect.effect_id == "infernal-wound" for effect in target.timed_effects)
    assert "poisoned" in target.active_effect_ids
