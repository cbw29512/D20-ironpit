from app.combat.action_economy import is_available
from app.combat.auras import resolve_start_turn_auras
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_catalog_2014 import load_catalog_2014
from app.content.monster_catalog_2014_reactions import reaction_start_turn_auras_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def test_unnerving_mask_parses_as_reaction_cost_fear_until_target_turn_end() -> None:
    source = next(item for item in load_catalog_2014() if item.id == "chain-devil")
    aura = reaction_start_turn_auras_2014(source)[0]
    assert (aura.range_ft, aura.save_dc, aura.save_ability) == (30, 14, "wisdom")
    assert aura.failure_condition_id == "frightened"
    assert aura.failure_expiry_timing == "target_turn_end"
    assert aura.reaction_cost is True


def test_reaction_cost_aura_spends_reaction_and_applies_frightened() -> None:
    aura_source = build_karnok_stoneward().model_copy(update={"start_turn_auras": [
        reaction_start_turn_auras_2014(next(item for item in load_catalog_2014() if item.id == "chain-devil"))[0]
    ]})
    source = EncounterCombatant(combatant_id="monster-1", side="monsters", position_ft=10, state=build_combatant_state(aura_source))
    target = EncounterCombatant(combatant_id="hero-1", side="heroes", position_ft=15, state=build_combatant_state(build_karnok_stoneward()))
    setup = EncounterSetup(heroes=[target], monsters=[source], hero_total_levels=1, monster_total_cr="1")
    events, _ = resolve_start_turn_auras(1, 1, target, setup, FixedDiceProvider([1]))
    assert len(events) == 1
    assert events[0].feature_id == "unnerving-mask"
    assert "frightened" in target.state.active_effect_ids
    assert not is_available(source.state, "reaction")
