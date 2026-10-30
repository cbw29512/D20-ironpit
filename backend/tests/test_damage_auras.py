from app.combat.auras import resolve_end_turn_damage_auras, resolve_start_turn_grapple_contact_damage
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_aura_source import fire_aura_source_is_fully_modeled, source_end_turn_damage_auras
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
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


def test_fire_elemental_fire_aura_ignition_is_source_bound_and_certified() -> None:
    try:
        elemental = build_combatant_from_capabilities("srd-fire-elemental")
        auras = source_end_turn_damage_auras("Fire Elemental")
        assert len(auras) == 1
        assert (auras[0].radius_ft, auras[0].damage_dice_count, auras[0].damage_dice_size) == (10, 1, 10)
        assert auras[0].applies_burning is True
        assert fire_aura_source_is_fully_modeled(_row("Fire Elemental")) is True
        assert audit_monster_source(elemental, _row("Fire Elemental")) == []
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Fire Elemental source-bound aura regression failed.")
        raise


def test_barbed_hide_compiles_and_damages_both_grapple_directions() -> None:
    try:
        barbed_template = build_combatant_from_capabilities("srd-barbed-devil")
        profile = barbed_template.start_turn_grapple_contact_damage
        assert profile is not None
        assert (profile.name, profile.damage_dice_count, profile.damage_dice_size) == (
            "Barbed Hide", 1, 10,
        )
        assert profile.damage_type.value == "piercing"

        hero_template = build_karnok_stoneward()
        for owner_grapples_target in (True, False):
            barbed = EncounterCombatant(
                combatant_id="barbed",
                side="monsters",
                position_ft=5,
                state=build_combatant_state(barbed_template),
            )
            hero = EncounterCombatant(
                combatant_id="hero",
                side="heroes",
                position_ft=0,
                state=build_combatant_state(hero_template),
            )
            if owner_grapples_target:
                apply_grapple(hero.state, "barbed", 13, 5)
            else:
                apply_grapple(barbed.state, "hero", 13, 5)
            setup = EncounterSetup(
                heroes=[hero],
                monsters=[barbed],
                hero_total_levels=1,
                monster_total_cr="5",
            )
            hp_before = hero.state.current_hp
            events, sequence = resolve_start_turn_grapple_contact_damage(
                1, 1, barbed, setup, FixedDiceProvider([6]),
            )

            assert sequence == 2
            assert len(events) == 1
            assert events[0].feature_id == "barbed-hide"
            assert events[0].damage_roll is not None
            assert events[0].damage_roll.total == 6
            assert hero.state.current_hp == hp_before - 6
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Barbed Hide grapple-contact regression failed.")
        raise
