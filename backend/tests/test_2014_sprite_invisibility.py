"""2014 Sprite: source-proven opening Invisible buff and shared expiry."""
from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.owner_action_expiry import expire_on_owner_event
from app.combat.precombat_buffs import prepare_opening_buffs
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_invisibility_2014 import source_invisibility_action_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.timed_self_buffs import TimedSelfBuffAction
from scripts.browser_template_serializer import template_row


def _sprite():
    return next(monster for monster in load_monster_source_2014() if monster.id == "sprite")


def _fight():
    sprite = _sprite()
    monster = EncounterCombatant(
        combatant_id="sprite", side="monsters", position_ft=0,
        state=build_combatant_state(compile_combatant(adapt_basic_monster_2014(sprite))),
    )
    hero = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=5,
        state=build_combatant_state(build_demo_fighter()),
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[monster], ruleset="2014",
        hero_total_levels=1, monster_total_cr="1/4",
    )
    return monster, hero, setup


def test_exact_source_binding_is_one_unlimited_concentration_self_buff() -> None:
    sprite = _sprite()
    snapshot = sprite.model_dump_json()
    actions = source_invisibility_action_2014(sprite)
    assert len(actions) == 1
    assert actions[0].id == "invisibility"
    assert actions[0].condition_ids == ["invisible"]
    assert actions[0].action_cost == "action"
    assert actions[0].resource_id is None
    assert actions[0].duration_rounds is None
    assert actions[0].concentration
    assert actions[0].magical_effect
    assert actions[0].ends_on_owner_attack and actions[0].ends_on_owner_spell_cast
    assert basic_blockers_2014(sprite) == ()
    template = compile_combatant(adapt_basic_monster_2014(sprite))
    row = template_row(template)["timed_self_buff_actions"][0]
    assert row["conditionIds"] == ["invisible"]
    assert row["magicalEffect"] is True
    assert row["endsOnOwnerAttack"] is True
    assert row["endsOnOwnerSpellCast"] is True
    assert row["resourceId"] is None
    assert row["durationRounds"] is None
    assert sprite.model_dump_json() == snapshot


def test_opening_invisibility_is_free_before_initiative_and_attack_ends_it() -> None:
    sprite, hero, setup = _fight()
    assert "invisible" not in sprite.state.active_effect_ids
    events, sequence = prepare_opening_buffs(setup)
    assert sequence == 2
    assert len(events) == 1
    assert events[0].round_number == 0
    assert events[0].feature_id == "invisibility"
    assert sprite.state.opening_buff_id == "invisibility"
    assert sprite.state.action_available is True
    assert sprite.state.concentration.effect_id == "invisibility"
    assert sprite.state.concentration.expires_round is None
    assert "invisible" in sprite.state.active_effect_ids
    assert sprite.state.timed_effects[0].ends_on_owner_attack
    assert sprite.state.timed_effects[0].source_is_magical
    assert "invisible" not in hero.state.active_effect_ids

    attack = resolve_attack(
        2, 1, sprite.state, hero.state, sprite.state.template.weapon_attack,
        5, FixedDiceProvider([10, 3, 3, 3]), actor_event_id="sprite",
        target_event_id="hero", affected_states=[sprite.state, hero.state],
    )
    assert attack.event_type == "attack"
    assert "invisible" not in sprite.state.active_effect_ids
    assert sprite.state.concentration is None
    assert not sprite.state.timed_effects
    assert "invisible" not in build_combatant_state(sprite.state.template).active_effect_ids


def test_spell_cast_expiry_and_fresh_fight_on_unrelated_renamed_self_buff() -> None:
    template = build_demo_fighter()
    source = TimedSelfBuffAction(
        id="custom-vanish", name="Renamed Shroud", condition_ids=["invisible"],
        magical_effect=True, concentration=True,
        ends_on_owner_attack=True, ends_on_owner_spell_cast=True,
    )
    template = template.model_copy(update={"timed_self_buff_actions": [source]})
    state = build_combatant_state(template)
    member = EncounterCombatant(combatant_id="caster", side="heroes", position_ft=0, state=state)
    resolve_timed_self_buff(1, 0, member, source, spend_action_cost=False)
    assert state.concentration.effect_id == "custom-vanish"
    assert expire_on_owner_event(state, "spell_cast", [state]) == ["invisible"]
    assert state.concentration is None
    assert "invisible" not in state.active_effect_ids
    assert not expire_on_owner_event(state, "spell_cast", [state])
    fresh = build_combatant_state(template)
    assert fresh.concentration is None
    assert "invisible" not in fresh.active_effect_ids


def test_mutating_printed_invisibility_does_not_get_source_admission() -> None:
    sprite = _sprite()
    mutated = sprite.model_copy(update={
        "source_actions": (sprite.source_actions or "").replace(
            "until it attacks or casts a spell", "until it attacks"
        ),
    })
    assert mutated.source_actions != sprite.source_actions
    assert source_invisibility_action_2014(mutated) == []
    assert "source:extra-action" in basic_blockers_2014(mutated)
