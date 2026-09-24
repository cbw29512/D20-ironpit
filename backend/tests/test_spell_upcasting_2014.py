from app.combat.spell_policy import SpellChoice, _slot_level
from app.combat.spell_resolution import _save_action
from app.combat.state import build_combatant_state
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014
from app.domain.encounters import EncounterCombatant


def test_pact_magic_uses_current_higher_slot_without_rewriting_printed_spell_level() -> None:
    template = build_varek_ashenmark_2014(9)
    fireball = next(action for action in template.spell_save_actions if action.id == "fireball")
    caster = EncounterCombatant(
        combatant_id="varek",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(template),
    )

    assert fireball.level == 3
    assert fireball.damage_dice_count == 8
    assert fireball.upcast_dice_per_level == 1
    assert {item.id: item.current_uses for item in caster.state.resources} == {
        "spell-slot-5": 2,
        "dark-ones-own-luck": 1,
    }

    cast_level = _slot_level(caster, fireball, "1:varek")
    assert cast_level == 5

    runtime_action = _save_action(
        SpellChoice(
            action=fireball,
            slot_level=cast_level,
            target_ids=(),
        ),
        caster.state,
    )
    assert runtime_action.damage_dice_count == 10
    assert runtime_action.damage_dice_size == 6
    assert runtime_action.damage_type == "fire"
