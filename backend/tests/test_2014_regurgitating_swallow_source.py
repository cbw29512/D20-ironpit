"""2014 regurgitating Swallow must be source-derived and fail closed."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_regurgitating_swallow_source_2014 import (
    source_proven_regurgitating_swallow_2014,
)


def test_exact_source_parameters_and_immutable_card():
    monsters = load_monster_source_2014()
    assert len(monsters) == 327
    monster = next(m for m in monsters if m.id == "behir")
    original = monster.model_dump_json()
    proof = source_proven_regurgitating_swallow_2014(monster)
    assert proof is not None
    assert proof.attack_id == "bite"
    assert proof.max_target_size == "medium"
    assert (proof.damage_dice_count, proof.damage_dice_size) == (6, 6)
    assert proof.damage_type == "acid"
    assert (proof.regurgitation_damage_threshold, proof.regurgitation_save_dc) == (30, 14)
    assert proof.regurgitation_save_ability == "constitution"
    assert (proof.regurgitation_range_ft, proof.exit_movement_ft) == (10, 15)
    assert monster.model_dump_json() == original


def test_changed_source_outcomes_are_rejected():
    monster = next(m for m in load_monster_source_2014() if m.id == "behir")
    for before, after in (
        ("30 damage or more", "20 damage or more"),
        ("DC 14 Constitution", "DC 13 Constitution"),
        ("one bite attack", "two bite attacks"),
        ("total cover", "half cover"),
        ("21 (6d6) acid", "21 (6d6) cold"),
        ("at the end of that turn", "at the start of that turn"),
        ("exiting prone", "exiting standing"),
    ):
        assert before in monster.source_actions
        changed = monster.model_copy(update={
            "source_actions": monster.source_actions.replace(before, after),
        })
        # Updated values are not silently reused from the original card.
        changed_proof = source_proven_regurgitating_swallow_2014(changed)
        assert changed_proof is None or changed_proof != source_proven_regurgitating_swallow_2014(monster)


def test_unrelated_simple_swallow_does_not_match():
    for monster in load_monster_source_2014():
        if monster.id in {"giant-frog", "giant-toad"}:
            assert source_proven_regurgitating_swallow_2014(monster) is None


def test_generic_action_and_fight_state_retain_regurgitation_rules():
    from app.content.demo import build_demo_fighter
    from app.combat.grapple import apply_grapple
    from app.combat.swallow_state import swallow_after_bite
    from app.combat.state import build_combatant_state
    from app.domain.swallow_actions import swallow_action_from_source
    from app.domain.size import CreatureSize

    monster = next(m for m in load_monster_source_2014() if m.id == "behir")
    proof = source_proven_regurgitating_swallow_2014(monster)
    assert proof is not None
    # The shared capability is parameterized, not keyed to the Behir name.
    action = swallow_action_from_source(proof)
    assert action.regurgitation_damage_threshold == 30
    assert action.regurgitation_save_dc == 14
    fighter = build_demo_fighter()
    bite = fighter.weapon_attack.model_copy(update={"id": "bite"})
    owner = build_combatant_state(fighter.model_copy(update={"weapon_attack": bite}))
    victim = build_combatant_state(fighter.model_copy(update={"size": CreatureSize.MEDIUM}))
    apply_grapple(victim, "generic-source", 16, 5, restrains=True)
    assert swallow_after_bite(
        "generic-source", owner, "victim", victim, action, bite_hit=True,
    )
    assert victim.swallowed.regurgitation_damage_threshold == 30
    assert victim.swallowed.regurgitation_save_dc == 14
    assert victim.swallowed.regurgitation_range_ft == 10


def test_behir_compiles_into_shared_runtime_and_browser_action():
    from app.content.monster_basic_candidates_2014 import basic_blockers_2014
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from app.content.capability_compiler import compile_combatant
    from scripts.browser_template_serializer import template_row

    source = next(m for m in load_monster_source_2014() if m.id == "behir")
    assert basic_blockers_2014(source) == ()
    compiled = compile_combatant(adapt_basic_monster_2014(source))
    assert len(compiled.swallow_actions) == 1
    rule = compiled.swallow_actions[0]
    assert rule.attack_id == "2014-behir-bite"
    assert rule.regurgitation_damage_threshold == 30
    assert rule.regurgitation_save_dc == 14
    row = template_row(compiled)["swallowActions"][0]
    assert row["regurgitationDamageThreshold"] == 30
    assert row["regurgitationSaveDc"] == 14
    assert row["damageDiceCount"] == 6
    assert row["damageDiceSize"] == 6
