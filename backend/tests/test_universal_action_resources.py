from app.combat.dice import FixedDiceProvider
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellAttackAction


def _member(combatant_id: str, side: str, position: int, armor_class: int = 10) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    template.armor_class = armor_class
    template.resources = []
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_shared_action_resource_resolves_explicit_before_fallback() -> None:
    member = _member("caster", "heroes", 0)
    member.state.template.resources = [
        ResourceDefinition(id="three-per-day", name="Three Per Day", max_uses=3),
        ResourceDefinition(id="spell-slot-1", name="Level 1 Slot", max_uses=2),
    ]
    member.state.resources = [
        type(member.state.resources).__args__[0](id="three-per-day", name="Three Per Day", current_uses=3, max_uses=3)
        if hasattr(type(member.state.resources), "__args__") else None
    ]
