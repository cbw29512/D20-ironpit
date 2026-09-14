from app.combat.offense_value import save_spell_expected_damage
from app.combat.saving_throw_rolls import saving_throw_mode
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.monster_spell_actions_2014 import _save_spell
from app.domain.encounters import EncounterCombatant
from app.domain.models import RollMode


def _target(creature_type: str) -> EncounterCombatant:
    template = build_goblin_warrior().model_copy(deep=True)
    template.creature_type = creature_type
    template.saving_throw_bonuses["constitution"] = 0
    return EncounterCombatant(
        combatant_id=creature_type, side="monsters", position_ft=30,
        state=build_combatant_state(template),
    )


def test_blight_declares_and_values_creature_type_rules() -> None:
    blight = _save_spell("blight", 4, 15, 7)
    assert blight.excluded_creature_types == ["undead", "construct"]
    assert blight.save_disadvantage_creature_types == ["plant"]
    assert blight.maximize_damage_creature_types == ["plant"]
    plant = _target("plant")
    assert saving_throw_mode(
        plant.state, "constitution", magical_effect=True, disadvantage_sources=1,
    ) is RollMode.DISADVANTAGE
    assert save_spell_expected_damage(_target("undead"), blight) == 0
    assert save_spell_expected_damage(plant, blight) > save_spell_expected_damage(_target("humanoid"), blight)
