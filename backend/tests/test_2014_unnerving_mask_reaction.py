from __future__ import annotations

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_unnerving_mask_2014 import supports_unnerving_mask_reaction_2014
from app.combat.action_economy import is_available
from app.combat.condition_rules import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.turn_start_save_condition_reaction import resolve_turn_start_save_condition_reactions
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _chain_devil():
    return next(m for m in load_monster_source_2014() if m.id == "chain-devil")


def test_source_proof_and_blocker_clears():
    monster = _chain_devil()
    assert supports_unnerving_mask_reaction_2014(monster)
    assert "source:reaction" not in basic_blockers_2014(monster)


def test_binding_produces_reaction():
    from app.content.monster_unnerving_mask_2014 import source_unnerving_mask_reaction_2014
    source = _chain_devil()
    reaction = source_unnerving_mask_reaction_2014(source)
    assert reaction is not None
    assert reaction.save_dc == 14
    assert reaction.save_ability == "wisdom"
    assert reaction.range_ft == 30
    assert reaction.condition_id == "frightened"
    assert reaction.expiry_timing == "target_turn_end"


def _minimal_state(name: str, reaction=None):
    from app.domain.combatants import CombatantTemplate
    from app.domain.runtime import CombatantState
    from app.domain.character_builds import AbilityScores
    from app.domain.movement import MovementModes
    template = CombatantTemplate(
        id=name.lower().replace(" ", "-"),
        name=name,
        archetype="test",
        kind="monster",
        size="medium",
        max_hp=10,
        armor_class=10,
        speed_ft=30,
        movement_modes=MovementModes(walk_ft=30),
        initiative_bonus=0,
        ability_scores=AbilityScores(strength=10, dexterity=10, constitution=10, intelligence=10, wisdom=10, charisma=10),
        turn_start_save_condition_reaction=reaction,
    )
    return CombatantState(template=template, current_hp=10)


def _setup_pair(distance: int = 10):
    from app.content.monster_unnerving_mask_2014 import source_unnerving_mask_reaction_2014
    reaction = source_unnerving_mask_reaction_2014(_chain_devil())
    devil = EncounterCombatant(
        combatant_id="devil", side="monsters", position_ft=0,
        state=_minimal_state("Chain Devil", reaction),
    )
    hero = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=distance,
        state=_minimal_state("Hero"),
    )
    setup = EncounterSetup(heroes=[hero], monsters=[devil], hero_total_levels=1, monster_total_cr="8")
    return devil, hero, setup


def test_failed_save_applies_frightened_and_spends_reaction():
    devil, hero, setup = _setup_pair(10)
    dice = FixedDiceProvider([1])
    events, _ = resolve_turn_start_save_condition_reactions(1, 1, hero, setup, dice)
    assert len(events) == 1
    assert events[0].save_succeeded is False
    assert "frightened" in events[0].applied_condition_ids
    assert has_condition(hero.state, "frightened")
    assert not is_available(devil.state, "reaction")


def test_success_does_not_apply():
    devil, hero, setup = _setup_pair(10)
    dice = FixedDiceProvider([20])
    events, _ = resolve_turn_start_save_condition_reactions(1, 1, hero, setup, dice)
    assert events[0].save_succeeded is True
    assert not has_condition(hero.state, "frightened")
    assert not is_available(devil.state, "reaction")


def test_out_of_range_skips():
    devil, hero, setup = _setup_pair(40)
    dice = FixedDiceProvider([1])
    events, _ = resolve_turn_start_save_condition_reactions(1, 1, hero, setup, dice)
    assert events == []
    assert is_available(devil.state, "reaction")
