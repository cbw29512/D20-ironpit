from app.combat.auras import resolve_end_turn_aura
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_aura_source_audit import parse_fire_aura
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _row(name):
    return next(row for row in load_monster_rows() if row["name"] == name)


def _member(cid, side, template, position):
    return EncounterCombatant(combatant_id=cid, side=side, position_ft=position, state=build_combatant_state(template))


def _setup(heroes, monsters):
    return EncounterSetup(heroes=heroes, monsters=monsters, hero_total_levels=1, monster_total_cr="2")


def test_azer_fire_aura_is_source_exact_and_fully_audited():
    template = build_combatant_from_capabilities("srd-azer-sentinel")
    assert template.creature_type == "elemental"
    assert template.end_turn_damage_aura == parse_fire_aura(_row("Azer Sentinel")["traits"])
    assert audit_monster_source(template, _row("Azer Sentinel")) == []


def test_fire_aura_uses_one_roll_and_independent_defenses():
    azer = build_combatant_from_capabilities("srd-azer-sentinel"); target = build_combatant_from_capabilities("srd-sahuagin-warrior")
    resistant = target.model_copy(update={"damage_resistances": ["fire"]})
    source = _member("m1", "monsters", azer, 5); normal = _member("h1", "heroes", target, 0); half = _member("h2", "heroes", resistant, 10); ally = _member("m2", "monsters", target, 5)
    events, sequence = resolve_end_turn_aura(1, 1, source, _setup([normal, half], [source, ally]), FixedDiceProvider([7]))
    assert sequence == 3 and [event.damage_roll.total for event in events] == [7, 3]
    assert normal.state.current_hp == target.max_hp - 7 and half.state.current_hp == target.max_hp - 3 and ally.state.current_hp == target.max_hp


def test_azer_aura_is_disabled_while_incapacitated():
    azer = build_combatant_from_capabilities("srd-azer-sentinel"); target = build_combatant_from_capabilities("srd-sahuagin-warrior")
    source = _member("m1", "monsters", azer, 5); source.state.is_unconscious = True; victim = _member("h1", "heroes", target, 0)
    events, sequence = resolve_end_turn_aura(1, 1, source, _setup([victim], [source]), FixedDiceProvider([7]))
    assert events == [] and sequence == 1 and victim.state.current_hp == target.max_hp


def test_fire_elemental_aura_fails_closed_until_ignition_is_modeled():
    assert "Fire Aura." in _row("Fire Elemental")["traits"]
    try: parse_fire_aura(_row("Fire Elemental")["traits"])
    except ValueError: pass
    else: raise AssertionError("Fire Elemental's richer Fire Aura must remain unsupported")
