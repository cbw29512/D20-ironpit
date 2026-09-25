from app.combat.offensive_ranges import offensive_ranges_for_target
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.offensive_spell_effects import build_guiding_bolt
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant


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


def test_spell_attack_range_remains_available_through_legal_upcast_slot() -> None:
    caster = _member("caster", "heroes", 0)
    target = _member("target", "monsters", 120)
    caster.state.template.spell_attack_actions = [build_guiding_bolt(5)]
    caster.state.resources = [
        ResourceDefinition(
            id="spell-slot-2",
            name="Level 2 Slot",
            max_uses=1,
        ).model_copy(update={"current_uses": 1}),
    ]

    ranges = offensive_ranges_for_target(caster, target, "1:caster")

    assert ("spell", 120) in ranges
