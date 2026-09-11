from app.combat.auras import resolve_end_turn_damage_auras
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_trait_source_audit import trait_issues
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _row(name: str):
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_azer_fire_aura_compiles_from_source_and_source_audits_cleanly() -> None:
    azer = build_combatant_from_capabilities("srd-azer-sentinel")
    assert len(azer.end_turn_damage_auras) == 1
    aura = azer.end_turn_damage_auras[0]
    assert (aura.name, aura.radius_ft, aura.damage_dice_count, aura.damage_dice_size) == ("Fire Aura", 5, 1, 10)
    assert aura.damage_type.value == "fire"
    assert aura.disabled_while_incapacitated is True
    assert audit_monster_source(azer, _row("Azer Sentinel")) == []


def test_fire_aura_uses_shared_damage_pipeline_at_end_of_turn() -> None:
    azer_template = build_combatant_from_capabilities("srd-azer-sentinel")
    hero_template = build_karnok_stoneward()
    azer = EncounterCombatant(
        combatant_id="azer", side="monsters", position_ft=5,
        state=build_combatant_state(azer_template),
    )
    hero = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=0,
        state=build_combatant_state(hero_template),
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[azer], hero_total_levels=1, monster_total_cr="2",
    )
    hp_before = hero.state.current_hp
    events, sequence = resolve_end_turn_damage_auras(1, 1, azer, setup, FixedDiceProvider([7]))
    assert sequence == 2
    assert len(events) == 1
    assert events[0].feature_id == "fire-aura"
    assert events[0].damage_roll is not None and events[0].damage_roll.total == 7
    assert hero.state.current_hp == hp_before - 7


def test_fire_elemental_extra_fire_aura_clause_remains_fail_closed() -> None:
    elemental = build_combatant_from_capabilities("srd-fire-elemental")
    issues = trait_issues(elemental, _row("Fire Elemental"))
    assert "trait-unmodeled-clause:fire-aura" in issues
