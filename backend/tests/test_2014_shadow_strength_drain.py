"""2014 Shadow: pinned source, generic on-hit reducer, and real attack resolution."""
from __future__ import annotations

from app.combat.ability_score_reduction import effective_ability_score
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.capability_attacks import AttackCapabilityDefinition
from app.domain.capability_effects import AbilityScoreReductionEffectDefinition, DiceSpec


def _shadow():
    return next(monster for monster in load_monster_source_2014() if monster.id == "shadow")


def _shadow_state():
    return build_combatant_state(compile_combatant(adapt_basic_monster_2014(_shadow())))


def _target():
    return build_combatant_state(build_commoner().model_copy(update={"max_hp": 100}))


def test_printed_shadow_is_admitted_and_ability_drain_is_compiled() -> None:
    monster = _shadow()
    before = monster.model_dump_json()
    attack = monster.attacks[0]
    assert (attack.name, attack.attack_bonus, attack.damage.dice_count,
            attack.damage.dice_size, attack.damage.bonus, attack.damage.type) == (
            "Strength Drain", 4, 2, 6, 2, "necrotic")
    assert attack.on_hit_ability_score_reduction == {
        "ability": "strength", "dice_count": 1, "dice_size": 4,
    }
    assert basic_blockers_2014(monster) == ()
    compiled = compile_combatant(adapt_basic_monster_2014(monster)).weapon_attack
    rider = compiled.on_hit_ability_score_reduction
    assert rider is not None
    assert (rider.source, rider.ability, rider.dice_count, rider.dice_size) == (
        "Strength Drain", "strength", 1, 4)
    assert monster.model_dump_json() == before


def test_source_proof_rejects_changed_numbers_and_missing_riders() -> None:
    monster = _shadow()
    attack = monster.attacks[0]
    variants = [
        monster.model_copy(update={"source_actions": monster.source_actions.replace("1d4", "1d6")}),
        monster.model_copy(update={"attacks": [attack.model_copy(update={
            "on_hit_ability_score_reduction": {"ability": "dexterity", "dice_count": 1, "dice_size": 4}
        })]}),
        monster.model_copy(update={"attacks": [attack.model_copy(update={
            "on_hit_ability_score_reduction": None
        })]}),
        monster.model_copy(update={"attacks": [attack.model_copy(update={
            "on_hit_ability_score_reduction": {"ability": "strength", "dice_count": 1, "dice_size": 0}
        })]}),
    ]
    for altered in variants:
        assert "attack:incomplete" in basic_blockers_2014(altered)


def test_renamed_homebrew_uses_identical_generic_effect() -> None:
    real = compile_combatant(adapt_basic_monster_2014(_shadow())).weapon_attack
    renamed = compile_attack(AttackCapabilityDefinition(
        id="homebrew-drain", name="Arbitrary Source", attack_kind="melee",
        attack_bonus=4, attack_ability="dexterity", damage=DiceSpec(count=2, size=6, bonus=2),
        damage_type="necrotic", animation="slash", effects=[
            AbilityScoreReductionEffectDefinition(
                source="Arbitrary Source", ability="strength", dice=DiceSpec(count=1, size=4),
            )
        ],
    ))
    left = real.on_hit_ability_score_reduction
    right = renamed.on_hit_ability_score_reduction
    assert left is not None and right is not None
    assert (left.ability, left.dice_count, left.dice_size) == (
        right.ability, right.dice_count, right.dice_size)
    assert left.source != right.source


def test_real_hits_stack_and_kill_at_strength_zero_without_zero_hp() -> None:
    attacker = _shadow_state()
    defender = _target()
    original = effective_ability_score(defender, "strength")
    assert original == 10
    for index, expected in enumerate([6, 2, 0], start=1):
        # One attack d20, two necrotic damage dice, then one d4 drain.
        hit = resolve_attack(
            index, index, attacker, defender, attacker.template.weapon_attack, 5,
            FixedDiceProvider([18, 1, 1, 4]), spend_action=False,
        )
        assert hit.hit and hit.attack_name == "Strength Drain"
        assert effective_ability_score(defender, "strength") == expected
        assert "Strength Drain" in hit.description
        if index < 3:
            assert defender.is_alive and not defender.is_dead
        else:
            assert defender.is_dead and defender.current_hp == 0
            assert defender.death_save_failures == 0
    assert defender.template.ability_scores.strength == original
    fresh = build_combatant_state(defender.template)
    assert effective_ability_score(fresh, "strength") == original
    assert fresh.ability_score_reductions == {}


def test_miss_never_drains() -> None:
    attacker = _shadow_state()
    defender = _target()
    before = effective_ability_score(defender, "strength")
    miss = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([1]), spend_action=False,
    )
    assert not miss.hit
    assert effective_ability_score(defender, "strength") == before
    assert defender.ability_score_reductions == {}
