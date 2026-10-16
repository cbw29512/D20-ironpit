"""Source-backed owner-grapple automatic-hit certification for 2014 attacks."""
from __future__ import annotations

import pytest

from app.combat.attack_legality import attack_allowed_against
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, release_grapple
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_grapple_auto_hit_source_2014 import source_proves_grapple_auto_hit_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014


def monster():
    return next(row for row in load_monster_source_2014() if row.id == "salamander")


def template_and_tail():
    template = compile_combatant(adapt_basic_monster_2014(monster()))
    tail = next(attack for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
                if attack.weapon.name == "Tail")
    return template, tail


def test_printed_tail_contract_source_admits_complete_salamander() -> None:
    source = monster()
    assert source_proves_grapple_auto_hit_2014(source, source.attacks[-1])
    assert basic_blockers_2014(source) == ()
    template, tail = template_and_tail()
    assert template.id == "2014-salamander"
    assert tail.grapple_target_policy == "auto_hit_own_grapple"
    assert tail.control_effect.grapple_escape_dc == 14
    assert tail.control_effect.restrains_while_grappled
    assert [(v.dice_count, v.dice_size, v.damage_type.value) for v in tail.on_hit_damage] == [
        (2, 6, "fire"),
    ]


@pytest.mark.parametrize("mutation", ["remove_autohit", "remove_target_lock", "remove_grapple"])
def test_printed_auto_hit_fails_closed_on_source_tampering(mutation: str) -> None:
    source = monster().model_copy(deep=True)
    if mutation == "remove_autohit":
        source.source_actions = source.source_actions.replace(
            "automatically hit the target", "try to hit the target",
        )
    elif mutation == "remove_target_lock":
        source.source_actions = source.source_actions.replace(
            "can't make tail attacks against other targets", "can hit any target",
        )
    else:
        source.attacks[-1].control_effect = None
    assert not source_proves_grapple_auto_hit_2014(source, source.attacks[-1])
    assert "attack:complex" in basic_blockers_2014(source)


def test_grapple_owner_auto_hit_resolves_both_damage_types_without_d20() -> None:
    source, tail = template_and_tail()
    actor = build_combatant_state(source)
    defender = build_combatant_state(build_aurelia_brightshield_2014(20))
    hp = defender.current_hp
    apply_grapple(defender, "attacker-1", 14, 10, restrains=True)
    assert attack_allowed_against(tail, "attacker-1", defender)
    event = resolve_attack(
        1, 1, actor, defender, tail, 5, FixedDiceProvider([1, 1, 1, 1]),
        actor_event_id="attacker-1", target_event_id="held", spend_action=False,
    )
    assert event.hit and not event.critical and event.attack_roll is None
    assert [part.damage_type.value for part in event.damage_components] == [
        "bludgeoning", "fire",
    ]
    assert event.damage_roll.total == 8
    assert defender.current_hp == hp - 8
    assert [x.source_id for x in defender.grapple_sources] == ["attacker-1"]


def test_auto_hit_stops_after_release_and_other_targets_remain_illegal() -> None:
    source, tail = template_and_tail()
    other = build_combatant_state(build_aurelia_brightshield_2014(20))
    held = build_combatant_state(build_aurelia_brightshield_2014(20))
    apply_grapple(held, "attacker-1", 14, 10, restrains=True)
    assert not attack_allowed_against(tail, "attacker-1", other, [other, held])
    release_grapple(held, "attacker-1")
    assert attack_allowed_against(tail, "attacker-1", other, [other, held])
    # Without owner-linked grapple, natural 1 still misses normally.
    event = resolve_attack(
        1, 1, build_combatant_state(source), other, tail, 5,
        FixedDiceProvider([1, 1]), actor_event_id="attacker-1",
        target_event_id="other", spend_action=False,
        affected_states=[other, held],
    )
    assert not event.hit and event.attack_roll is not None
    assert not other.grapple_sources


@pytest.mark.parametrize("condition", ["incapacitated", "unconscious", "stunned", "paralyzed", "petrified"])
def test_incapacitated_grappler_cannot_attack_even_when_attack_is_free(condition: str) -> None:
    actor_template, tail = template_and_tail()
    actor = build_combatant_state(actor_template)
    defender = build_combatant_state(build_aurelia_brightshield_2014(20))
    apply_grapple(defender, "attacker-1", 14, 10, restrains=True)
    actor.active_effect_ids.append(condition)
    with pytest.raises(RuntimeError, match="Attack resolution failed"):
        resolve_attack(
            1, 1, actor, defender, tail, 5, FixedDiceProvider([1, 1, 1]),
            actor_event_id="attacker-1", spend_action=False,
        )
    assert defender.current_hp == defender.template.max_hp

