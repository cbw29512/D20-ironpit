from app.combat.aura_activation import expire_active_auras, resolve_ready_activated_aura
from app.combat.auras import resolve_start_turn_auras
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monster_catalog_2014 import compile_monster_2014, load_catalog_2014, unsupported_mechanics_2014
from app.content.monster_catalog_2014_action_support import limited_action_uses_2014
from app.content.monster_catalog_2014_auras import activated_start_turn_auras_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition


def _source(monster_id: str):
    return next(row for row in load_catalog_2014() if row.id == monster_id)


def _member(monster_id: str, combatant_id: str, side: str, x: int) -> EncounterCombatant:
    template = compile_monster_2014(_source(monster_id))
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=1)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=x * 5, state=state)


def test_dretch_fetid_cloud_uses_generic_activated_aura_contract() -> None:
    source = _source("dretch")
    aura = activated_start_turn_auras_2014(source.source_actions)[0]
    assert aura.id == "fetid-cloud"
    assert aura.name == "Fetid Cloud"
    assert aura.range_ft == 10
    assert aura.save_ability == "constitution"
    assert aura.save_dc == 11
    assert aura.activation_cost == "action"
    assert aura.activation_duration_rounds == 10
    assert aura.resource_id == "fetid-cloud"
    assert aura.failure_condition_id == "poisoned"
    assert aura.failure_blocks_reactions is True
    assert aura.failure_action_bonus_exclusive is True
    assert aura.area_lightly_obscured is True
    assert aura.spreads_around_corners is True
    assert aura.dispersed_by_strong_wind is True
    assert limited_action_uses_2014(source)["fetid-cloud"] == 1
    assert unsupported_mechanics_2014(source) == []


def test_dretch_fetid_cloud_activation_save_effect_log_and_expiry() -> None:
    dretch = _member("dretch", "monster-1:dretch", "monsters", 1)
    goblin = _member("goblin", "hero-1:goblin", "heroes", 2)
    setup = EncounterSetup(
        heroes=[goblin], monsters=[dretch], hero_total_levels=1, monster_total_cr="1/4",
        map_definition=BattleMapDefinition(id="test", width_squares=10, height_squares=10),
    )

    activation_events, sequence, fired = resolve_ready_activated_aura(1, 1, dretch, setup)
    assert fired is True
    assert sequence == 2
    assert activation_events[0].feature_id == "fetid-cloud"
    assert "Dretch uses Fetid Cloud" in activation_events[0].description
    assert dretch.state.action_available is False
    assert next(item for item in dretch.state.resources if item.id == "fetid-cloud").current_uses == 0
    assert dretch.state.active_auras[0].expires_round == 11

    save_events, sequence = resolve_start_turn_auras(
        sequence, 1, goblin, setup, FixedDiceProvider([1]),
    )
    assert sequence == 3
    assert len(save_events) == 1
    assert save_events[0].actor_name == "Dretch"
    assert save_events[0].feature_id == "fetid-cloud"
    assert "Dretch's Fetid Cloud" in save_events[0].description
    effect = next(item for item in goblin.state.timed_effects if item.source_effect_id == "fetid-cloud")
    assert effect.effect_id == "poisoned"
    assert effect.blocks_reactions is True
    assert effect.action_bonus_exclusive is True
    assert effect.expiry_timing == "target_turn_start"

    expiry_events, sequence = expire_active_auras(sequence, 11, dretch)
    assert len(expiry_events) == 1
    assert "Dretch's Fetid Cloud ends" in expiry_events[0].description
    assert dretch.state.active_auras == []
