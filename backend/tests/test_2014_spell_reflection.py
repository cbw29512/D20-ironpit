from app.combat.action_economy import is_available
from app.combat.dice import FixedDiceProvider
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.spell_policy import SpellChoice
from app.combat.spell_resolution import resolve_spell
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.offensive_spell_effects import build_guiding_bolt
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.reactions import SpellReflectionReaction
from app.domain.spells import SpellSaveAction


def _member(combatant_id: str, side: str, position: int, *, reflector: bool = False) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"; template.name = combatant_id
    if reflector:
        template.spell_reflection_reaction = SpellReflectionReaction(range_ft=30)
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_successful_single_target_save_spell_reflects_to_caster() -> None:
    caster = _member("caster", "heroes", 0)
    reflector = _member("reflector", "monsters", 30, reflector=True)
    caster.state.template.saving_throw_bonuses["dexterity"] = 0
    reflector.state.template.saving_throw_bonuses["dexterity"] = 20
    setup = EncounterSetup(heroes=[caster], monsters=[reflector], hero_total_levels=1, monster_total_cr="1")
    spell = SpellSaveAction(
        id="test-bolt", name="Test Bolt", level=0, range_ft=60,
        save_ability="dexterity", dc=12, damage_dice_count=2, damage_dice_size=6,
        damage_type="fire", success_damage="none",
    )
    before_reflector = reflector.state.current_hp; before_caster = caster.state.current_hp
    events, _ = resolve_spell(
        1, 1, caster, setup, SpellChoice(spell, 0, (reflector.combatant_id,)), "1:caster",
        FixedDiceProvider([2, 1, 4, 4]),
    )
    save_event = events[-1]
    assert save_event.target_id == caster.combatant_id
    assert "uses Spell Reflection" in save_event.description
    assert reflector.state.current_hp == before_reflector
    assert caster.state.current_hp == before_caster - 8
    assert not is_available(reflector.state, "reaction")


def test_missed_spell_attack_reflects_and_rerolls_against_caster() -> None:
    caster = _member("caster", "heroes", 0)
    reflector = _member("reflector", "monsters", 30, reflector=True)
    reflector.state.template.armor_class = 30
    spell = build_guiding_bolt(5)
    caster.state.template.spell_attack_actions = [spell]
    caster.state.template.resources = [ResourceDefinition(id="spell-slot-1", name="Level 1 Slot", max_uses=1)]
    caster.state = build_combatant_state(caster.state.template)
    setup = EncounterSetup(heroes=[caster], monsters=[reflector], hero_total_levels=1, monster_total_cr="1")
    before = caster.state.current_hp
    event = resolve_spell_attack(
        1, 1, caster, reflector, spell, setup, "1:caster",
        FixedDiceProvider([5, 15, 1, 1, 1, 1]),
    )
    assert event.target_id == caster.combatant_id
    assert event.hit is True
    assert "uses Spell Reflection" in event.description
    assert caster.state.current_hp == before - 4
    assert not is_available(reflector.state, "reaction")
