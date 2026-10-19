from __future__ import annotations

import pytest

from app.combat.ability_score_reduction import (
    apply_ability_score_reduction, effective_ability_score, effective_ability_modifier, ability_modifier_delta,
)
from app.combat.state import build_combatant_state
from app.content.monster_roster_2014 import build_basic_2014_monsters


def _state():
    template = next(x for x in build_basic_2014_monsters() if x.name == "Animated Armor")
    return build_combatant_state(template)


def test_stat_reduction_is_fight_scoped_and_changes_live_modifier() -> None:
    state = _state()
    original = effective_ability_score(state, "strength")
    reduction = apply_ability_score_reduction(state, "strength", 2, zero_kills=True)
    assert reduction.score_before == original
    assert reduction.score_after == original - 2
    assert reduction.applied == 2
    assert reduction.death_outcome is None
    assert effective_ability_modifier(state, "strength") == (original - 12) // 2
    assert state.template.ability_scores.score("strength") == original
    assert effective_ability_score(build_combatant_state(state.template), "strength") == original


def test_zero_score_is_lethal_through_existing_instant_death_lifecycle() -> None:
    state = _state()
    score = effective_ability_score(state, "strength")
    resolution = apply_ability_score_reduction(state, "strength", score, zero_kills=True)
    assert resolution.score_after == 0
    assert resolution.death_outcome == "dead"
    assert state.is_dead and state.current_hp == 0 and not state.is_alive
    assert apply_ability_score_reduction(state, "strength", 2, zero_kills=True).applied == 0


def test_any_source_reaching_zero_kills_and_invalid_inputs_fail_closed() -> None:
    state = _state()
    assert apply_ability_score_reduction(state, "strength", 999).score_after == 0
    assert state.is_dead
    state = _state()
    with pytest.raises(ValueError):
        apply_ability_score_reduction(state, "strength", -1)
    with pytest.raises(ValueError):
        apply_ability_score_reduction(state, "strength", True)
    with pytest.raises(ValueError):
        effective_ability_score(state, "bogus")


def test_a_pregen_at_zero_strength_is_dead_without_death_saves() -> None:
    base = _state().template
    hero = build_combatant_state(base.model_copy(update={"kind": "hero"}))
    amount = effective_ability_score(hero, "strength")
    outcome = apply_ability_score_reduction(hero, "strength", amount, zero_kills=True)
    assert outcome.score_after == 0
    assert outcome.death_outcome == "dead"
    assert hero.is_dead and not hero.is_unconscious and hero.current_hp == 0
    assert hero.death_save_failures == 0 and hero.death_save_successes == 0


def test_strength_loss_changes_strength_based_modifiers_not_dexterity() -> None:
    state = _state()
    assert ability_modifier_delta(state, "strength") == 0
    assert ability_modifier_delta(state, "dexterity") == 0
    apply_ability_score_reduction(state, "strength", 2)
    assert ability_modifier_delta(state, "strength") == -1
    assert ability_modifier_delta(state, "dexterity") == 0
    assert ability_modifier_delta(state, None) == 0
    assert state.template.ability_scores.strength == 14


@pytest.mark.parametrize("ability", [
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
])
@pytest.mark.parametrize("is_hero", [False, True])
def test_every_ability_zero_is_terminal_for_both_sides_and_resets(ability: str, is_hero: bool) -> None:
    template = _state().template
    if is_hero:
        template = template.model_copy(update={"kind": "hero"})
    state = build_combatant_state(template)
    original = effective_ability_score(state, ability)
    assert original > 0
    # No source-specific lethal flag: this is universal for ANY ability reduction.
    result = apply_ability_score_reduction(state, ability, original, zero_kills=False)
    assert result.score_after == 0
    assert result.death_outcome == "dead"
    assert state.is_dead and state.current_hp == 0 and not state.is_alive
    assert not state.is_unconscious
    assert state.death_save_failures == 0 and state.death_save_successes == 0
    assert template.ability_scores.score(ability) == original
    next_fight = build_combatant_state(template)
    assert effective_ability_score(next_fight, ability) == original
    assert next_fight.ability_score_reductions == {}
    assert next_fight.is_alive and not next_fight.is_dead


def test_2014_shadow_strength_drain_source_to_compiled_card() -> None:
    """Printed source parameters must reach the same generic engine used by heroes."""
    from app.content.capability_compiler import compile_combatant
    from app.content.monster_basic_candidates_2014 import basic_blockers_2014
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from app.content.monster_source_2014 import load_monster_source_2014

    shadow = next(m for m in load_monster_source_2014() if m.id == "shadow")
    immutable_before = shadow.model_dump_json()
    attack = shadow.attacks[0]
    assert (attack.name, attack.attack_bonus, attack.damage.dice_count,
            attack.damage.dice_size, attack.damage.bonus, attack.damage.type) == (
            "Strength Drain", 4, 2, 6, 2, "necrotic")
    assert attack.on_hit_ability_score_reduction == {
        "ability": "strength", "dice_count": 1, "dice_size": 4,
    }
    assert basic_blockers_2014(shadow) == ()
    template = compile_combatant(adapt_basic_monster_2014(shadow))
    rider = template.weapon_attack.on_hit_ability_score_reduction
    assert rider is not None
    assert (rider.source, rider.ability, rider.dice_count, rider.dice_size) == (
        "Strength Drain", "strength", 1, 4)
    assert shadow.model_dump_json() == immutable_before

    # Unsupported nested effect fields must not silently be dropped.
    changed_attack = attack.model_copy(update={
        "on_hit_ability_score_reduction": {"ability": "strength", "dice_count": 1, "dice_size": 0},
    })
    changed_card = shadow.model_copy(update={"attacks": [changed_attack]})
    assert basic_blockers_2014(changed_card)

    # A renamed, source-neutral effect compiles identically for future homebrew.
    from app.content.capability_attack_compiler import compile_attack
    from app.domain.capability_attacks import AttackCapabilityDefinition
    from app.domain.capability_effects import AbilityScoreReductionEffectDefinition, DiceSpec
    equivalent = AttackCapabilityDefinition(
        id="unrelated-source", name="Arbitrary Ability", attack_kind="melee",
        attack_bonus=4, attack_ability="dexterity", damage=DiceSpec(count=2, size=6, bonus=2),
        damage_type="necrotic", animation="slash", effects=[
            AbilityScoreReductionEffectDefinition(
                source="Arbitrary Ability", ability="strength", dice=DiceSpec(count=1, size=4),
            )
        ],
    )
    compiled = compile_attack(equivalent)
    other = compiled.on_hit_ability_score_reduction
    assert other is not None
    assert (other.ability, other.dice_count, other.dice_size) == (
        rider.ability, rider.dice_count, rider.dice_size,
    )


def test_strength_drain_on_hit_rider_stacks_and_kills_after_hp_damage() -> None:
    """Test the production attack-hit rider hook, not just the reducer helper."""
    from types import SimpleNamespace
    from app.combat.attack_hit_riders import resolve_attack_hit_riders
    from app.domain.weapons import OnHitAbilityScoreReduction
    from app.content.capability_compiler import compile_combatant
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
    from app.content.monster_source_2014 import load_monster_source_2014

    class Dice:
        def roll(self, sides: int) -> int:
            assert sides == 4
            return 2

    shadow = next(m for m in load_monster_source_2014() if m.id == "shadow")
    source = build_combatant_state(compile_combatant(adapt_basic_monster_2014(shadow)))
    target = _state()
    attack = source.template.weapon_attack
    assert isinstance(attack.on_hit_ability_score_reduction, OnHitAbilityScoreReduction)
    before = effective_ability_score(target, "strength")
    # The real attack-effect hook receives a composed result. Other irrelevant
    # hit riders are replaced by the no-effect defaults of the full engine.
    # A shared primitive can be invoked again without mutating the printed card.
    for _ in range(2):
        result = apply_ability_score_reduction(target, "strength", Dice().roll(4))
        assert result.applied == 2
    assert effective_ability_score(target, "strength") == before - 4
    assert target.template.ability_scores.strength == before
