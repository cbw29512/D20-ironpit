import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.modifier_stack import effective_armor_class
from app.combat.precombat_spells import choose_defensive_spell, prepare_defenses
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.spell_effects import SHIELD_OF_FAITH
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import DefensiveSpellAction


def _defense(spell_id: str, level: int, priority: int = 0):
    return DefensiveSpellAction(
        id=spell_id, name=spell_id.title(), level=level, duration_minutes=60,
        temporary_hp=5, temporary_hp_per_slot_above=5, priority=priority,
    )


def _caster(spells, slots):
    base = build_karnok_stoneward()
    resources = [ResourceDefinition(id=f"spell-slot-{level}", name=f"Level {level} Slot", max_uses=count) for level, count in slots.items()]
    template = base.model_copy(update={"defensive_spell_actions": spells, "resources": resources})
    return EncounterCombatant(combatant_id="caster", side="heroes", position_ft=0, state=build_combatant_state(template))


def _setup(caster):
    enemy = EncounterCombatant(
        combatant_id="enemy", side="monsters", position_ft=5,
        state=build_combatant_state(build_goblin_warrior()),
    )
    return EncounterSetup(heroes=[caster], monsters=[enemy], hero_total_levels=1, monster_total_cr="1/4")


def test_precombat_uses_one_declared_defense_and_printed_level_slot() -> None:
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


def test_precombat_does_not_use_higher_level_slot_when_upcasting_is_deferred() -> None:
    caster = _caster([_defense("false-life-like", 1)], {3: 1})
    events, sequence = prepare_defenses(_setup(caster))
    assert events == []
    assert sequence == 1
    assert caster.state.temporary_hp == 0
    assert next(item for item in caster.state.resources if item.id == "spell-slot-3").current_uses == 1
    assert choose_defensive_spell(caster) is None


def test_concentration_defense_rejects_anonymous_lifecycle_effects() -> None:
    with pytest.raises(ValueError, match="source-owned modifier effects"):
        DefensiveSpellAction(
            id="unsafe", name="Unsafe", level=1, duration_minutes=10,
            temporary_hp=5, concentration=True,
        )


def test_precombat_defense_can_apply_temporary_resistance() -> None:
    spell = DefensiveSpellAction(
        id="resist-fire", name="Resist Fire", level=1, duration_minutes=60,
        damage_resistances=["fire"], priority=1,
    )
    caster = _caster([spell], {1: 1})
    prepare_defenses(_setup(caster))
    assert [item.value for item in caster.state.temporary_damage_resistances] == ["fire"]


def test_shield_of_faith_uses_real_modifier_attack_and_concentration_paths() -> None:
    caster = _caster([SHIELD_OF_FAITH], {1: 1})
    setup = _setup(caster)
    events, _ = prepare_defenses(setup)
    enemy = setup.monsters[0]

    assert SHIELD_OF_FAITH.action_cost == "bonus_action"
    assert SHIELD_OF_FAITH.range_ft == 60
    assert SHIELD_OF_FAITH.duration_minutes == 10
    assert events[0].feature_id == "shield-of-faith"
    assert caster.state.concentration is not None
    assert caster.state.concentration.effect_id == "shield-of-faith"
    assert effective_armor_class(caster.state) == caster.state.template.armor_class + 2
    assert next(item for item in caster.state.resources if item.id == "spell-slot-1").current_uses == 0

    dice = FixedDiceProvider([14, 16, 1, 1])
    miss = resolve_encounter_attack(
        2, 1, enemy, caster, enemy.state.template.weapon_attack, 5, dice, setup, spend_action=False,
    )
    assert miss.hit is False
    assert caster.state.concentration is not None

    hit = resolve_encounter_attack(
        3, 1, enemy, caster, enemy.state.template.weapon_attack, 5, dice, setup, spend_action=False,
    )
    assert hit.hit is True
    assert caster.state.concentration is None
    assert caster.state.active_modifiers == []
    assert effective_armor_class(caster.state) == caster.state.template.armor_class
