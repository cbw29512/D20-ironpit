from app.combat.offensive_ranges import offensive_ranges_for_target
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.runtime import ResourceState
from app.domain.encounters import EncounterCombatant
from app.domain.spells import SpellSaveAction


def _member(combatant_id: str, side: str, position: int) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_save_spell_range_remains_available_through_legal_upcast_slot() -> None:
    caster = _member("caster", "heroes", 0)
    target = _member("target", "monsters", 60)
    caster.state.template.spell_save_actions = [
        SpellSaveAction(
            id="scaling-save",
            name="Scaling Save",
            level=1,
            action_cost="action",
            range_ft=60,
            save_ability="dexterity",
            dc=13,
            damage_dice_count=2,
            damage_dice_size=6,
            damage_type="fire",
            success_damage="half",
            upcast_dice_per_level=1,
        ),
    ]
    caster.state.resources = [
        ResourceState(
            id="spell-slot-2",
            name="Level 2 Slot",
            current_uses=1,
            max_uses=1,
        ),
    ]

    ranges = offensive_ranges_for_target(caster, target, "1:caster")

    assert ("spell", 60) in ranges
