from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.effect_removal import choose_effect_removal_action, resolve_effect_removal
from app.combat.modifier_stack import add_modifier
from app.combat.state import build_combatant_state
from app.content.monk_open_hand_2014_runtime import build_kael_stillwater_2014
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _hostile_spell_source() -> EncounterCombatant:
    spell = DefensiveSpellAction(
        id="hostile-test-spell",
        name="Hostile Test Spell",
        level=4,
        range_ft=30,
        duration_minutes=1,
        target_policy="friendly",
        modifier_effects=[SpellModifierEffect(kind="armor-class", flat_bonus=-1)],
    )
    template = build_commoner().model_copy(update={
        "ruleset": "2014",
        "defensive_spell_actions": [spell],
    })
    return _member(template, "enemy-caster", "monsters", 10)


def test_level_14_is_incremental_and_adds_three_cleansing_touch_uses() -> None:
    level13 = build_aurelia_brightshield_2014(13)
    hero = build_aurelia_brightshield_2014(14)
    profile = build_aurelia_brightshield_2014_profile(14)

    assert hero.max_hp == level13.max_hp + 8
    assert hero.ability_scores == level13.ability_scores
    assert {item.id: item.max_uses for item in hero.resources if item.id.startswith("spell-slot-")} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
    }
    cleansing = next(item for item in hero.resources if item.id == "cleansing-touch")
    assert cleansing.max_uses == hero.ability_scores.modifier("charisma") == 3
    assert hero.effect_removal_actions[0].id == "cleansing-touch"
    assert hero.effect_removal_actions[0].level == 0
    assert hero.effect_removal_actions[0].range_ft == 5
    assert hero.effect_removal_actions[0].target_mode == "self_or_ally"
    assert hero.effect_removal_actions[0].auto_remove_max_level == 9
    assert hero.effect_removal_actions[0].casting_ability is None
    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["cleansing-touch"].automated is True


def test_cleansing_touch_removes_opposing_spell_without_stripping_friendly_buff() -> None:
    paladin = _member(build_aurelia_brightshield_2014(14), "aurelia", "heroes", 0)
    ally = _member(build_kael_stillwater_2014(1), "ally", "heroes", 5)
    enemy = _hostile_spell_source()
    setup = EncounterSetup(
        heroes=[paladin, ally],
        monsters=[enemy],
        hero_total_levels=15,
        monster_total_cr="0",
        ruleset="2014",
    )

    add_modifier(ally.state, CombatModifier(
        id="aurelia:death-ward:ally:0",
        source_id=paladin.combatant_id,
        source_effect_id="death-ward",
        source_name="Death Ward",
        source_is_magical=True,
        kind=ModifierKind.ZERO_HP_REPLACEMENT,
        replacement_hp=1,
        prevents_instant_death=True,
        target_id=ally.combatant_id,
    ))
    add_modifier(ally.state, CombatModifier(
        id="enemy:hostile-test-spell:ally:0",
        source_id=enemy.combatant_id,
        source_effect_id="hostile-test-spell",
        source_name="Hostile Test Spell",
        source_is_magical=True,
        kind=ModifierKind.ARMOR_CLASS,
        flat_bonus=-1,
        target_id=ally.combatant_id,
    ))

    before_slots = {
        item.id: item.current_uses
        for item in paladin.state.resources
        if item.id.startswith("spell-slot-")
    }
    cleansing_resource = next(item for item in paladin.state.resources if item.id == "cleansing-touch")
    assert cleansing_resource.current_uses == 3

    choice = choose_effect_removal_action(paladin, setup, "1:aurelia")
    assert choice is not None
    action, effect = choice
    assert action.id == "cleansing-touch"
    assert effect.target.combatant_id == ally.combatant_id
    assert effect.source.combatant_id == enemy.combatant_id
    assert effect.effect_id == "hostile-test-spell"

    event = resolve_effect_removal(
        1, 1, paladin, setup, action, effect, FixedDiceProvider([1]), "1:aurelia",
    )

    assert paladin.state.action_available is False
    assert cleansing_resource.current_uses == 2
    assert event.ability_check_roll is None
    assert event.check_dc is None
    assert event.removed_condition_ids == ["hostile-test-spell"]
    assert not any(item.source_effect_id == "hostile-test-spell" for item in ally.state.active_modifiers)
    assert any(item.source_effect_id == "death-ward" for item in ally.state.active_modifiers)
    assert {
        item.id: item.current_uses
        for item in paladin.state.resources
        if item.id.startswith("spell-slot-")
    } == before_slots
