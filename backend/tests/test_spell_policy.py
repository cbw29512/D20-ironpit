from app.combat.dice import FixedDiceProvider
from app.combat.spell_policy import choose_spell
from app.combat.spell_resolution import resolve_spell
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction


def _spell(spell_id: str, level: int, radius: int | None = None, upcast: int = 0):
    return SpellSaveAction(
        id=spell_id, name=spell_id.title(), level=level, range_ft=150,
        area_radius_ft=radius, save_ability="dexterity", dc=12,
        damage_dice_count=1, damage_dice_size=6, damage_type="fire",
        success_damage="half", upcast_dice_per_level=upcast,
    )


def _caster(spells, slots):
    base = build_karnok_stoneward()
    resources = [ResourceDefinition(id=f"spell-slot-{level}", name=f"Level {level} Slot", max_uses=count) for level, count in slots.items()]
    template = base.model_copy(update={"spell_save_actions": spells, "resources": resources})
    return EncounterCombatant(combatant_id="caster", side="heroes", position_ft=0, state=build_combatant_state(template))


def _monster(index: int, position: int):
    # Synthetic enemy uses Karnok's complete certified six-save profile. Spell tests must never infer a missing save bonus.
    return EncounterCombatant(
        combatant_id=f"monster-{index}", side="monsters", position_ft=position,
        state=build_combatant_state(build_karnok_stoneward()),
    )


def _ally(index: int, position: int):
    return EncounterCombatant(
        combatant_id=f"ally-{index}", side="heroes", position_ft=position,
        state=build_combatant_state(build_karnok_stoneward()),
    )


def _setup(caster, monsters, allies=()):
    heroes = [caster, *allies]
    return EncounterSetup(
        heroes=heroes, monsters=list(monsters), hero_total_levels=len(heroes),
        monster_total_cr="1",
    )


def test_highest_level_safe_spell_is_chosen_first() -> None:
    caster = _caster([_spell("fireball", 3, 20), _spell("lower-bolt", 2)], {3: 1, 2: 2})
    setup = _setup(caster, [_monster(i, 30) for i in range(4)])
    choice = choose_spell(caster, setup, "1:caster")
    assert choice is not None
    assert choice.action.id == "fireball"
    assert choice.slot_level == 3
    assert len(choice.target_ids) == 4


def test_unsafe_high_level_aoe_falls_through_to_lower_spell() -> None:
    caster = _caster([_spell("fireball", 3, 10), _spell("lower-bolt", 2)], {3: 1, 2: 1})
    setup = _setup(caster, [_monster(0, 5), _monster(1, 5)], [_ally(1, 0)])
    choice = choose_spell(caster, setup, "1:caster")
    assert choice is not None
    assert choice.action.id == "lower-bolt"


def test_resolving_aoe_spends_one_slot_and_hits_friends_too() -> None:
    caster = _caster([_spell("fireball", 3, 20)], {3: 1})
    setup = _setup(caster, [_monster(i, 5) for i in range(3)])
    choice = choose_spell(caster, setup, "1:caster")
    assert choice is not None
    events, sequence = resolve_spell(
        1, 1, caster, setup, choice, "1:caster",
        FixedDiceProvider([1, 6, 1, 6, 1, 6, 1, 6]),
    )
    assert sequence == 6
    assert len(events) == 5
    assert events[0].feature_id == "fireball"
    assert "3 enemies and 1 unprotected allies" in events[0].description
    assert {event.target_id for event in events[1:]} == {"caster", "monster-0", "monster-1", "monster-2"}
    slot = next(item for item in caster.state.resources if item.id == "spell-slot-3")
    assert slot.current_uses == 0
    assert caster.state.action_available is False


def test_high_slot_upcasts_and_one_slot_spell_gate_still_applies() -> None:
    caster = _caster([_spell("fireball", 3, 20, upcast=1), _spell("spark", 0)], {4: 1})
    setup = _setup(caster, [_monster(i, 30) for i in range(3)])
    choice = choose_spell(caster, setup, "1:caster")
    assert choice is not None and choice.slot_level == 4
    mark_slot_spell_cast(caster.state, "1:caster")
    next_choice = choose_spell(caster, setup, "1:caster")
    assert next_choice is not None
    assert next_choice.action.id == "spark"
    assert next_choice.slot_level == 0
