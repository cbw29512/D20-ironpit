from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.state import build_combatant_state
from app.combat.timed_auras import resolve_enemy_start_turn_auras, resolve_timed_aura_activation
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.saving_throw_context import SavingThrowContext


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def test_holy_nimbus_activates_and_deals_generic_enemy_start_turn_damage() -> None:
    paladin = _member(build_aurelia_brightshield_2014(20), "paladin", "heroes", 4, 4)
    enemy_template = build_commoner().model_copy(update={"ruleset": "2014", "max_hp": 30})
    enemy = _member(enemy_template, "enemy", "monsters", 8, 4)
    setup = EncounterSetup(
        heroes=[paladin],
        monsters=[enemy],
        hero_total_levels=20,
        monster_total_cr="0",
        ruleset="2014",
        map_definition=build_standard_iron_pit_map(),
    )
    action = paladin.state.template.timed_aura_actions[0]
    event = resolve_timed_aura_activation(1, 1, paladin, action)
    assert event.feature_id == "holy-nimbus"
    assert next(item for item in paladin.state.resources if item.id == "holy-nimbus").current_uses == 0

    before = enemy.state.current_hp
    events, sequence = resolve_enemy_start_turn_auras(2, 1, enemy, setup)
    assert sequence == 3
    assert len(events) == 1
    assert events[0].feature_id == "holy-nimbus"
    assert events[0].damage_components[0].damage_type.value == "radiant"
    assert enemy.state.current_hp == before - 10


def test_holy_nimbus_save_advantage_requires_spell_and_fiend_or_undead_source() -> None:
    paladin = _member(build_aurelia_brightshield_2014(20), "paladin", "heroes", 4, 4)
    action = paladin.state.template.timed_aura_actions[0]
    resolve_timed_aura_activation(1, 1, paladin, action)

    fiend_spell = SavingThrowContext(source_is_spell=True, source_creature_type="Fiend")
    undead_spell = SavingThrowContext(source_is_spell=True, source_creature_type="Undead")
    humanoid_spell = SavingThrowContext(source_is_spell=True, source_creature_type="Humanoid")
    fiend_feature = SavingThrowContext(source_is_spell=False, source_creature_type="Fiend")

    assert saving_throw_mode(paladin.state, "dexterity", fiend_spell).value == "advantage"
    assert saving_throw_mode(paladin.state, "wisdom", undead_spell).value == "advantage"
    assert saving_throw_mode(paladin.state, "dexterity", humanoid_spell).value == "normal"
    assert saving_throw_mode(paladin.state, "dexterity", fiend_feature).value == "normal"
