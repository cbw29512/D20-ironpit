from __future__ import annotations

from app.combat.landing_offense_policy import decide_post_move_offense
from app.combat.persistent_save_zone_cast import choose_save_zone_action
from app.combat.spell_policy import choose_spell
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=abs(x) * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def _setup(caster: EncounterCombatant, enemy: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[caster],
        monsters=[enemy],
        hero_total_levels=caster.state.template.level,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )


def test_insect_plague_is_bound_as_a_damaging_save_zone_not_forced_over_flame_strike() -> None:
    caster = _member(build_seraphine_dawnshield_level(9), "seraphine", "heroes", 1, 7)
    enemy = _member(build_commoner().model_copy(update={"max_hp": 40}, deep=True), "enemy", "monsters", 9, 7)
    setup = _setup(caster, enemy)
    begin_turn(caster.state)
    plague = next(item for item in caster.state.template.persistent_save_zone_actions if item.id == "insect-plague")
    assert plague.damage_dice_count == 4
    assert plague.damage_dice_size == 10
    assert plague.radius_ft == 20
    assert choose_save_zone_action(caster, setup, "1:seraphine") is None

    choice = choose_spell(caster, setup, "1:seraphine")
    assert choice is not None
    assert choice.action.id == "flame-strike"
    pick = decide_post_move_offense(caster, setup, "1:seraphine")
    assert pick.family == "spell"
    assert pick.expected_damage > 4 * 5.5


def test_insect_plague_is_selected_only_when_it_is_the_most_damage_that_can_land() -> None:
    caster = _member(build_seraphine_dawnshield_level(9), "seraphine", "heroes", 1, 7)
    enemy = _member(build_commoner().model_copy(update={"max_hp": 40}, deep=True), "enemy", "monsters", 18, 7)
    setup = _setup(caster, enemy)
    begin_turn(caster.state)
    assert choose_spell(caster, setup, "1:seraphine") is None
    pick = decide_post_move_offense(caster, setup, "1:seraphine")
    assert pick.family == "save-zone"
    action, _center = pick.payload
    assert action.id == "insect-plague"
    assert pick.expected_damage == 4 * 5.5
