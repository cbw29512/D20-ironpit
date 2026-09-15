from app.combat.dice import FixedDiceProvider
from app.combat.start_turn_damage import (
    apply_on_hit_ongoing_damage,
    clear_magical_healing,
    resolve_start_turn_ongoing_damage,
    should_skip_on_hit_save,
)
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.actions import GrappleSource
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.on_hit_saves import OnHitSaveEffect
from app.domain.ongoing_damage import OngoingDamageEffect
from app.domain.weapons import DamageType


def _member(combatant_id: str, side: str, *, resistant: bool = False) -> EncounterCombatant:
    update = {"max_hp": 100}
    if resistant: update["damage_resistances"] = [DamageType.PIERCING]
    template = build_goblin_warrior().model_copy(deep=True, update=update)
    state = build_combatant_state(template)
    return EncounterCombatant(combatant_id=combatant_id, side=side, position_ft=0, state=state)


def _attack(effect: OngoingDamageEffect, *, save: bool = False):
    attack = build_goblin_warrior().weapon_attack.model_copy(deep=True)
    return attack.model_copy(update={
        "id": "tail" if save else "chain",
        "ongoing_damage_effect": effect,
        "on_hit_save_effect": OnHitSaveEffect(
            save_ability="constitution", dc=17, excluded_creature_types=["undead", "construct"],
            gates_ongoing_damage=True,
        ) if save else None,
    })


def test_infernal_wound_stacks_and_loses_hp_without_consuming_temporary_hp() -> None:
    target = _member("hero", "heroes")
    source = _member("devil", "monsters")
    target.state.temporary_hp = 10
    effect = OngoingDamageEffect(
        id="infernal-wound", name="Infernal Wound", dice_count=3, dice_size=6,
        apply_on="failed_on_hit_save", stacks_on_reapply=True, ends_on_magical_healing=True,
        removal_ability="wisdom", removal_skill="medicine", removal_dc=12,
    )
    attack = _attack(effect, save=True)
    assert apply_on_hit_ongoing_damage(target.state, attack, source.combatant_id, False)
    assert should_skip_on_hit_save(target.state, attack, source.combatant_id)
    assert apply_on_hit_ongoing_damage(target.state, attack, source.combatant_id, None)
    setup = EncounterSetup(heroes=[target], monsters=[source], hero_total_levels=1, monster_total_cr="1")
    events, _ = resolve_start_turn_ongoing_damage(1, 2, target, setup, FixedDiceProvider([1, 2, 3, 4, 5, 6]))
    assert events[0].damage_roll.total == 21
    assert target.state.current_hp == 79
    assert target.state.temporary_hp == 10
    assert events[0].damage_components == []
    assert clear_magical_healing(target.state) == ["infernal-wound"]
    assert target.state.ongoing_damage_effects == []


def test_grapple_ongoing_damage_uses_damage_defenses_and_ends_with_grapple() -> None:
    target = _member("hero", "heroes", resistant=True)
    source = _member("devil", "monsters")
    effect = OngoingDamageEffect(
        id="grapple-start-turn-damage", name="Chain grapple", dice_count=2, dice_size=6,
        damage_type="piercing", ends_when_grapple_source_ends=True,
    )
    attack = _attack(effect)
    target.state.grapple_sources.append(GrappleSource(
        source_id=source.combatant_id, source_effect_id=attack.id, escape_dc=14, restrains=True,
    ))
    assert apply_on_hit_ongoing_damage(target.state, attack, source.combatant_id, None)
    setup = EncounterSetup(heroes=[target], monsters=[source], hero_total_levels=1, monster_total_cr="1")
    events, sequence = resolve_start_turn_ongoing_damage(1, 2, target, setup, FixedDiceProvider([4, 4]))
    assert sequence == 2
    assert events[0].damage_components[0].total == 8
    assert events[0].damage_components[0].applied_total == 4
    assert target.state.current_hp == 96
    target.state.grapple_sources.clear()
    events, _ = resolve_start_turn_ongoing_damage(2, 3, target, setup, FixedDiceProvider([6, 6]))
    assert events == []
    assert target.state.ongoing_damage_effects == []
