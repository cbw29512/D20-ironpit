from app.combat.automatic_damage_spell_resolution import resolve_automatic_damage_spell
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.automatic_damage_spells import AutomaticDamageSpellAction
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.weapons import DamageType


def _member(combatant_id: str, side: str, position: int, *, caster: bool = False):
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    template.resources = []
    template.automatic_damage_spell_actions = []
    if caster:
        template.resources = [
            ResourceDefinition(id="spell-slot-1", name="Level 1 Slots", max_uses=1),
            ResourceDefinition(id="spell-slot-2", name="Level 2 Slots", max_uses=1),
        ]
        template.automatic_damage_spell_actions = [AutomaticDamageSpellAction(
            id="magic-missile", name="Magic Missile", level=1, range_ft=120,
            base_projectiles=3, projectiles_per_slot_above=1,
            damage_dice_count_per_projectile=1, damage_dice_size=4,
            damage_bonus_per_projectile=1, damage_type="force",
        )]
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_magic_missile_automatically_hits_and_spends_lowest_slot() -> None:
    caster = _member("caster", "heroes", 0, caster=True)
    target = _member("target", "monsters", 30)
    setup = EncounterSetup(heroes=[caster], monsters=[target], hero_total_levels=1, monster_total_cr="1")
    spell = caster.state.template.automatic_damage_spell_actions[0]

    event = resolve_automatic_damage_spell(
        1, 1, caster, target, spell, setup, "1:caster", FixedDiceProvider([1, 2, 4]),
    )

    assert event.attack_roll is None and event.saving_throw_roll is None
    assert event.damage_roll is not None and event.damage_roll.total == 10
    assert len(event.damage_components) == 3
    assert caster.state.resources[0].current_uses == 0
    assert caster.state.resources[1].current_uses == 1
    assert caster.state.action_available is False


def test_magic_missile_upcasts_and_applies_resistance_per_projectile() -> None:
    caster = _member("caster", "heroes", 0, caster=True)
    caster.state.resources[0].current_uses = 0
    target = _member("target", "monsters", 30)
    target.state.template.damage_resistances = [DamageType.FORCE]
    setup = EncounterSetup(heroes=[caster], monsters=[target], hero_total_levels=1, monster_total_cr="1")
    spell = caster.state.template.automatic_damage_spell_actions[0]

    event = resolve_automatic_damage_spell(
        1, 1, caster, target, spell, setup, "1:caster", FixedDiceProvider([4, 4, 4, 4]),
    )

    assert event.damage_roll is not None and event.damage_roll.total == 8
    assert len(event.damage_components) == 4
    assert all(component.applied_total == 2 for component in event.damage_components)
    assert caster.state.resources[1].current_uses == 0
