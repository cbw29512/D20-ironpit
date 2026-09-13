from app.combat.aura_modifiers import attack_advantage_sources, saving_throw_advantage_sources
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _row(name: str):
    return next(row for row in load_monster_rows() if row["name"] == name)


def _member(combatant_id: str, side: str, position: int, template):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_hobgoblin_captain_compiles_authority_aura_from_source() -> None:
    captain = build_combatant_from_capabilities("srd-hobgoblin-captain")
    assert len(captain.roll_advantage_auras) == 1
    aura = captain.roll_advantage_auras[0]
    assert (aura.name, aura.radius_ft, aura.target_scope) == ("Aura of Authority", 10, "self-and-allies")
    assert aura.attack_roll_advantage and aura.saving_throw_advantage
    assert aura.disabled_while_incapacitated
    assert audit_monster_source(captain, _row("Hobgoblin Captain")) == []


def test_roll_advantage_aura_respects_side_range_and_incapacitation() -> None:
    captain_template = build_combatant_from_capabilities("srd-hobgoblin-captain")
    ally_template = build_combatant_from_capabilities("srd-hobgoblin-warrior")
    captain = _member("captain", "monsters", 0, captain_template)
    ally = _member("ally", "monsters", 10, ally_template)
    enemy = _member("enemy", "heroes", 5, ally_template)
    setup = EncounterSetup(heroes=[enemy], monsters=[captain, ally], hero_total_levels=1, monster_total_cr="7/2")

    assert attack_advantage_sources(captain, setup) == 1
    assert attack_advantage_sources(ally, setup) == 1
    assert saving_throw_advantage_sources(ally, setup) == 1
    assert attack_advantage_sources(enemy, setup) == 0

    ally.position_ft = 15
    assert attack_advantage_sources(ally, setup) == 0
    ally.position_ft = 10
    captain.state.active_effect_ids.append("incapacitated")
    assert attack_advantage_sources(captain, setup) == 0
    assert saving_throw_advantage_sources(ally, setup) == 0
