"""Universal encounter-only swallow transitions for Giant Frog / Giant Toad."""
from __future__ import annotations

from app.combat.grapple import apply_grapple
from app.combat.swallow_lifecycle import source_turn_swallowed_damage, release_invalid_swallowed
from app.combat.swallow_state import swallow_after_bite
from app.combat.state import build_combatant_state
from app.combat.dice import FixedDiceProvider
from app.content.demo import build_demo_fighter
from app.content.monster_grapple_swallow_source_2014 import source_grapple_swallow_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.size import CreatureSize
from app.domain.swallow_actions import swallow_action_from_source


def _make(monster_id: str):
    source = next(m for m in load_monster_source_2014() if m.id == monster_id)
    action = swallow_action_from_source(source_grapple_swallow_2014(source))
    assert action is not None
    fighter = build_demo_fighter()
    attack = fighter.weapon_attack.model_copy(update={"id": "bite"})
    owner_template = fighter.model_copy(update={"weapon_attack": attack})
    target_template = fighter.model_copy(update={"size": CreatureSize.SMALL})
    owner, target = build_combatant_state(owner_template), build_combatant_state(target_template)
    return source, action, owner, target


def test_swallow_requires_live_hit_owned_grapple_target_size_and_slot():
    source, action, owner, target = _make("giant-frog")
    before = source.model_dump_json()
    assert not swallow_after_bite("frog", owner, "victim", target, action, bite_hit=True)
    apply_grapple(target, "frog", 11, 5, restrains=True)
    assert not swallow_after_bite("frog", owner, "victim", target, action, bite_hit=False)
    assert swallow_after_bite("frog", owner, "victim", target, action, bite_hit=True)
    assert target.swallowed.source_id == "frog"
    assert target.grapple_sources == []
    assert "restrained" in target.active_effect_ids
    assert "blinded" in target.active_effect_ids
    assert owner.swallowed_target_ids == ["victim"]
    assert not swallow_after_bite("frog", owner, "victim", target, action, bite_hit=True)
    assert source.model_dump_json() == before


def test_frog_size_restriction_and_toad_size_limit():
    _, frog, owner, target = _make("giant-frog")
    target.template = target.template.model_copy(update={"size": CreatureSize.MEDIUM})
    apply_grapple(target, "frog", 11, 5, restrains=True)
    assert not swallow_after_bite("frog", owner, "victim", target, frog, bite_hit=True)
    assert target.swallowed is None
    _, toad, owner2, medium = _make("giant-toad")
    medium.template = medium.template.model_copy(update={"size": CreatureSize.MEDIUM})
    apply_grapple(medium, "toad", 13, 5, restrains=True)
    assert swallow_after_bite("toad", owner2, "medium", medium, toad, bite_hit=True)


def test_owner_turn_acid_damage_and_source_death_release():
    _, action, owner, target = _make("giant-frog")
    apply_grapple(target, "frog", 11, 5, restrains=True)
    assert swallow_after_bite("frog", owner, "victim", target, action, bite_hit=True)
    eater = EncounterCombatant(combatant_id="frog", side="monsters", position_ft=0, state=owner)
    meal = EncounterCombatant(combatant_id="victim", side="heroes", position_ft=0, state=target)
    setup = EncounterSetup(heroes=[meal], monsters=[eater], hero_total_levels=1, monster_total_cr="1/4")
    hp = target.current_hp
    events, next_sequence = source_turn_swallowed_damage(
        1, 2, eater, setup, FixedDiceProvider([3, 4])
    )
    assert len(events) == 1 and next_sequence == 2
    assert events[0].target_id == "victim"
    assert target.current_hp == hp - 7
    owner.is_alive = False
    owner.is_dead = True
    owner.current_hp = 0
    assert release_invalid_swallowed(setup) == ["victim"]
    assert target.swallowed is None
    assert owner.swallowed_target_ids == []
    assert "blinded" not in target.active_effect_ids
    assert "restrained" not in target.active_effect_ids
    assert "prone" in target.active_effect_ids
    assert release_invalid_swallowed(setup) == []


def test_swallowed_target_has_total_cover_from_external_attacks():
    from app.combat.attack_legality import attack_allowed_against

    _, action, owner, target = _make("giant-toad")
    target.template = target.template.model_copy(update={"size": CreatureSize.MEDIUM})
    apply_grapple(target, "toad", 13, 5, restrains=True)
    assert swallow_after_bite("toad", owner, "victim", target, action, bite_hit=True)
    attack = owner.template.weapon_attack
    assert not attack_allowed_against(attack, "outside-attacker", target, [owner, target])
    assert not attack_allowed_against(attack, "toad", target, [owner, target])


def test_real_admitted_frog_resolves_its_compiled_bite_then_swallows():
    from app.combat.encounter_swallow_action import resolve_swallow_action
    from app.content.capability_compiler import compile_combatant
    from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014

    source = next(m for m in load_monster_source_2014() if m.id == "giant-frog")
    frog_state = build_combatant_state(compile_combatant(adapt_basic_monster_2014(source)))
    victim_template = build_demo_fighter().model_copy(update={"size": CreatureSize.SMALL})
    victim_state = build_combatant_state(victim_template)
    frog = EncounterCombatant(combatant_id="frog", side="monsters", position_ft=0, state=frog_state)
    victim = EncounterCombatant(combatant_id="victim", side="heroes", position_ft=5, state=victim_state)
    setup = EncounterSetup(heroes=[victim], monsters=[frog], hero_total_levels=1, monster_total_cr="1/4")
    apply_grapple(victim_state, "frog", 11, 5, restrains=True)

    result = resolve_swallow_action(
        1, 1, frog, setup, FixedDiceProvider([20, 19, 1, 1]),
    )
    assert result is not None
    events, sequence = result
    assert sequence == 2 and events[0].hit
    assert victim_state.swallowed is not None
    assert victim_state.swallowed.source_id == "frog"
    assert frog_state.swallowed_target_ids == ["victim"]
