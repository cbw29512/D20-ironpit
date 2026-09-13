from app.combat.dice import FixedDiceProvider
from app.combat.resources import action_resource_available, spend_action_resource
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.runtime import ResourceState
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


def _install_resources(member: EncounterCombatant) -> None:
    member.state.template.resources = [
        ResourceDefinition(id="three-per-day", name="Three Per Day", max_uses=3),
        ResourceDefinition(id="spell-slot-1", name="Level 1 Slot", max_uses=2),
    ]
    member.state.resources = [
        ResourceState(id="three-per-day", name="Three Per Day", current_uses=3, max_uses=3),
        ResourceState(id="spell-slot-1", name="Level 1 Slot", current_uses=2, max_uses=2),
    ]


def test_shared_action_resource_prefers_explicit_resource_over_fallback() -> None:
    member = _member("caster", "heroes", 0)
    _install_resources(member)

    assert action_resource_available(
        member.state, "three-per-day", 1, fallback_resource_id="spell-slot-1",
    ) is True
    assert spend_action_resource(
        member.state, "three-per-day", 1, fallback_resource_id="spell-slot-1",
    ) == 2
    assert member.state.resources[0].current_uses == 2
    assert member.state.resources[1].current_uses == 2


def test_explicit_limited_use_spell_attack_does_not_consume_spell_slot_gate() -> None:
    caster = _member("caster", "heroes", 0)
    target = _member("target", "monsters", 30, armor_class=10)
    _install_resources(caster)
    setup = EncounterSetup(heroes=[caster], monsters=[target], hero_total_levels=1, monster_total_cr="1")
    spell = SpellAttackAction(
        id="innate-bolt",
        name="Innate Bolt",
        level=1,
        action_cost="action",
        resource_id="three-per-day",
        resource_cost=1,
        attack_kind="ranged",
        range_ft=120,
        attack_bonus=5,
        damage_dice_count=1,
        damage_dice_size=8,
        damage_type="force",
    )

    event = resolve_spell_attack(
        1, 1, caster, target, spell, setup, "1:caster", FixedDiceProvider([15, 4]),
    )

    assert event.hit is True
    assert event.resource_remaining == 2
    assert caster.state.resources[0].current_uses == 2
    assert caster.state.resources[1].current_uses == 2
    assert caster.state.spell_slot_expended_turn_key is None
