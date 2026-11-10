"""Balor 2014 full source admission and universal attack behavior."""
from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.models import RollMode
from scripts.browser_template_serializer import template_row


def _balor():
    return next(m for m in load_monster_source_2014() if m.id == "balor")


def _attacks():
    template = compile_combatant(adapt_basic_monster_2014(_balor()))
    attacks = {
        x.weapon.name: x for x in [template.weapon_attack, *template.alternate_weapon_attacks]
    }
    return template, attacks


def _member(template, uid, side, x):
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=1)
    return EncounterCombatant(combatant_id=uid, side=side, position_ft=x * 5, state=state)


def test_balor_is_complete_with_exact_2014_attack_data_and_browser_export():
    m = _balor()
    frozen = m.model_dump_json()
    assert basic_blockers_2014(m) == ()
    template, attacks = _attacks()
    assert set(attacks) >= {"Longsword", "Whip"}
    sword, whip = attacks["Longsword"], attacks["Whip"]
    assert sword.critical_dice_multiplier == 3
    assert (sword.attack_bonus, sword.weapon.reach_ft, sword.weapon.dice_count,
            sword.weapon.dice_size, sword.damage_bonus) == (14, 10, 3, 8, 8)
    assert len(sword.on_hit_damage) == 1
    assert (sword.on_hit_damage[0].dice_count, sword.on_hit_damage[0].dice_size,
            sword.on_hit_damage[0].damage_type.value) == (3, 8, "lightning")
    assert (whip.attack_bonus, whip.weapon.reach_ft, whip.weapon.dice_count,
            whip.weapon.dice_size, whip.damage_bonus) == (14, 30, 2, 6, 8)
    assert len(whip.on_hit_damage) == 1 and whip.on_hit_damage[0].damage_type.value == "fire"
    assert whip.on_hit_condition_save.save_ability == "strength"
    assert whip.on_hit_condition_save.dc == 20
    assert whip.on_hit_condition_save.condition_id is None
    assert whip.on_hit_condition_save.failure_pull_ft == 25
    assert len(template.multiattack_slots) == 2
    rows = {x["name"]: x for x in template_row(template)["attacks"]}
    assert rows["Longsword"]["criticalDiceMultiplier"] == 3
    assert rows["Whip"]["onHitConditionSave"]["failurePullFt"] == 25
    assert m.model_dump_json() == frozen


def test_triple_critical_rolls_every_printed_typed_die_not_the_flat_bonus():
    template, attacks = _attacks()
    source = build_combatant_state(template)
    ordinary, parts = resolve_weapon_damage(
        source, attacks["Longsword"], FixedDiceProvider([2] * 6),
        False, RollMode.NORMAL, "1:source",
    )
    assert [len(part.rolls) for part in parts] == [3, 3]
    assert ordinary.total == 20
    critical, parts = resolve_weapon_damage(
        source, attacks["Longsword"], FixedDiceProvider([2] * 18),
        True, RollMode.NORMAL, "1:source",
    )
    assert [len(part.rolls) for part in parts] == [9, 9]
    assert [part.total for part in parts] == [26, 18]
    assert critical.total == 44


def test_whip_uses_save_not_contest_and_pulls_only_on_failure():
    _, attacks = _attacks()
    actor_template = build_commoner().model_copy(update={"max_hp": 200, "name": "Unrelated attacker"})
    target_template = build_commoner().model_copy(update={"max_hp": 200, "name": "Unrelated target"})
    for save, should_move in [(1, True), (20, False)]:
        actor = _member(actor_template, "actor", "monsters", 1)
        target = _member(target_template, "target", "heroes", 6)
        setup = EncounterSetup(
            heroes=[target], monsters=[actor], hero_total_levels=1,
            monster_total_cr="1/4",
            map_definition=BattleMapDefinition(
                id="source-save-pull", width_squares=10, height_squares=4,
            ),
        )
        event = resolve_attack(
            1, 1, actor.state, target.state, attacks["Whip"], 25,
            FixedDiceProvider([15, 2, 2, 2, 2, 2, save]),
            actor_event_id="actor", target_event_id="target", spend_action=False,
            reaction_setup=setup,
        )
        assert event.hit is True
        assert event.save_dc == 20 and event.save_ability == "strength"
        assert event.save_succeeded is (not should_move)
        assert target.state.position == GridPosition(x=2 if should_move else 6, y=1)
        assert not target.state.active_effect_ids
        assert ("pulled 20 feet toward" in event.description) is should_move


def test_source_mutations_fail_closed_and_renamed_cards_keep_mechanics():
    m = _balor()
    renamed = m.model_copy(update={"id": "alternate-source", "name": "Other Creature"})
    for attack in m.attacks:
        bound = source_completed_mixed_attack_2014(renamed, attack)
        assert bound.source_complete
    for before, after in (
        ("rolls damage dice three times", "rolls damage dice four times"),
        ("DC 20 Strength saving throw", "DC 17 Strength saving throw"),
        ("pulled up to 25 feet", "pushed up to 25 feet"),
    ):
        mutated = m.model_copy(update={
            "source_actions": m.source_actions.replace(before, after),
        })
        assert mutated.source_actions != m.source_actions
        assert "attack:incomplete" in basic_blockers_2014(mutated)
