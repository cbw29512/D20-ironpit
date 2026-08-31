from app.combat.precombat_spells import choose_defensive_spell, prepare_defenses
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import DefensiveSpellAction


def _defense(spell_id: str, level: int, priority: int = 0, concentration: bool = False):
    return DefensiveSpellAction(
        id=spell_id, name=spell_id.title(), level=level, duration_minutes=60,
        temporary_hp=5, temporary_hp_per_slot_above=5,
        concentration=concentration, priority=priority,
    )


def _caster(spells, slots):
    base = build_karnok_stoneward()
    resources = [ResourceDefinition(id=f"spell-slot-{level}", name=f"Level {level} Slot", max_uses=count) for level, count in slots.items()]
    template = base.model_copy(update={"defensive_spell_actions": spells, "resources": resources})
    return EncounterCombatant(combatant_id="caster", side="heroes", position_ft=0, state=build_combatant_state(template))


def _setup(caster):
    enemy = EncounterCombatant(
        combatant_id="enemy", side="monsters", position_ft=30,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    return EncounterSetup(heroes=[caster], monsters=[enemy], hero_total_levels=1, monster_total_cr="1")


def test_precombat_uses_one_declared_defense_and_lowest_legal_slot() -> None:
    caster = _caster([_defense("preferred", 1, priority=10), _defense("backup", 2)], {1: 1, 3: 1})
    events, sequence = prepare_defenses(_setup(caster))
    assert sequence == 2
    assert len(events) == 1
    assert events[0].feature_id == "preferred"
    assert caster.state.temporary_hp == 5
    assert next(item for item in caster.state.resources if item.id == "spell-slot-1").current_uses == 0
    assert next(item for item in caster.state.resources if item.id == "spell-slot-3").current_uses == 1
    assert caster.state.action_available is True
    assert caster.state.bonus_action_available is True


def test_precombat_upcasts_when_only_higher_slot_is_available() -> None:
    caster = _caster([_defense("false-life-like", 1)], {3: 1})
    prepare_defenses(_setup(caster))
    assert caster.state.temporary_hp == 15
    assert next(item for item in caster.state.resources if item.id == "spell-slot-3").current_uses == 0


def test_concentration_defense_fails_closed_until_concentration_is_certified() -> None:
    caster = _caster([_defense("concentration-defense", 1, priority=20, concentration=True), _defense("safe-defense", 1)], {1: 1})
    choice = choose_defensive_spell(caster)
    assert choice is not None
    assert choice[0].id == "safe-defense"


def test_precombat_defense_can_apply_temporary_resistance() -> None:
    spell = DefensiveSpellAction(
        id="resist-fire", name="Resist Fire", level=1, duration_minutes=60,
        damage_resistances=["fire"], priority=1,
    )
    caster = _caster([spell], {1: 1})
    prepare_defenses(_setup(caster))
    assert [item.value for item in caster.state.temporary_damage_resistances] == ["fire"]
