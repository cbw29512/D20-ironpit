from app.combat.dice import FixedDiceProvider
from app.combat.spell_policy import SpellChoice
from app.combat.spell_resolution import resolve_spell
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction


def _member(side: str, index: int, position: int) -> EncounterCombatant:
    template = build_karnok_stoneward() if side == "heroes" else build_goblin_warrior()
    return EncounterCombatant(
        combatant_id=f"{side}-{index}", side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_simultaneous_save_spell_rolls_damage_once_for_all_targets() -> None:
    caster = _member("heroes", 0, 0)
    monsters = [_member("monsters", index, 30) for index in range(2)]
    for monster in monsters:
        monster.state.template.saving_throw_bonuses["dexterity"] = 0
    setup = EncounterSetup(
        heroes=[caster], monsters=monsters, hero_total_levels=1,
        monster_total_cr="1/2", starting_distance_ft=30,
    )
    spell = SpellSaveAction(
        id="shared-flame", name="Shared Flame", level=0, range_ft=60, area_radius_ft=10,
        save_ability="dexterity", dc=10, damage_dice_count=2, damage_dice_size=6,
        damage_type="fire", success_damage="half",
    )
    choice = SpellChoice(spell, 0, ("monsters-0", "monsters-1"))
    events, _ = resolve_spell(
        1, 1, caster, setup, choice, "heroes-0:round-1",
        FixedDiceProvider([1, 4, 4, 20]),
    )

    saves = [event for event in events if event.event_type == "saving_throw"]
    assert len(saves) == 2
    assert saves[0].save_succeeded is False
    assert saves[1].save_succeeded is True
    assert saves[0].damage_components[0].rolls == [4, 4]
    assert saves[1].damage_components[0].rolls == [4, 4]
    assert saves[0].damage_roll is not None and saves[0].damage_roll.total == 8
    assert saves[1].damage_roll is not None and saves[1].damage_roll.total == 4
