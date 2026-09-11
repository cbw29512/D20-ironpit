from app.combat.dice import FixedDiceProvider
from app.combat.start_turn_auras import resolve_start_turn_save_condition_auras
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _row(name: str):
    return next(row for row in load_monster_rows() if row["name"] == name)


def _member(template, combatant_id: str, side: str, position_ft: int):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position_ft,
        state=build_combatant_state(template),
    )


def test_hezrou_source_compiles_to_generic_stench_aura_and_audits_clean() -> None:
    hezrou = build_combatant_from_capabilities("srd-hezrou")
    assert hezrou.magic_resistance is True
    assert len(hezrou.start_turn_save_condition_auras) == 1
    aura = hezrou.start_turn_save_condition_auras[0]
    assert (aura.name, aura.radius_ft, aura.save_ability, aura.dc) == ("Stench", 10, "constitution", 16)
    assert (aura.condition, aura.expiry_timing) == ("poisoned", "target_turn_start")
    assert audit_monster_source(hezrou, _row("Hezrou")) == []


def test_start_turn_aura_failed_save_applies_timed_condition() -> None:
    hezrou_template = build_combatant_from_capabilities("srd-hezrou")
    wolf_template = build_combatant_from_capabilities("srd-wolf")
    hezrou = _member(hezrou_template, "hezrou", "monsters", 0)
    wolf = _member(wolf_template, "wolf", "heroes", 10)
    setup = EncounterSetup(
        heroes=[wolf], monsters=[hezrou], hero_total_levels=1, monster_total_cr="8",
    )
    events, sequence = resolve_start_turn_save_condition_auras(
        1, 1, wolf, setup, FixedDiceProvider([1]),
    )
    assert sequence == 2 and len(events) == 1
    assert events[0].feature_id == "stench" and events[0].save_succeeded is False
    assert "poisoned" in wolf.state.active_effect_ids
    effect = next(effect for effect in wolf.state.timed_effects if effect.effect_id == "poisoned")
    assert effect.source_id == "hezrou" and effect.expiry_timing == "target_turn_start"


def test_start_turn_aura_does_not_reach_beyond_emanation() -> None:
    hezrou_template = build_combatant_from_capabilities("srd-hezrou")
    wolf_template = build_combatant_from_capabilities("srd-wolf")
    hezrou = _member(hezrou_template, "hezrou", "monsters", 0)
    wolf = _member(wolf_template, "wolf", "heroes", 15)
    setup = EncounterSetup(
        heroes=[wolf], monsters=[hezrou], hero_total_levels=1, monster_total_cr="8",
    )
    events, sequence = resolve_start_turn_save_condition_auras(
        1, 1, wolf, setup, FixedDiceProvider([1]),
    )
    assert events == [] and sequence == 1
    assert "poisoned" not in wolf.state.active_effect_ids
