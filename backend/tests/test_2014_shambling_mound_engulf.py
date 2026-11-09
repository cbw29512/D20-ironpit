"""Shambling Mound: source proof and generic two-hit grapple combat."""
from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.grapple import release_grapple, resolve_escape_grapple
from app.combat.encounter_grapple_upgrade_action import resolve_grapple_upgrade_action
from app.combat.multi_hit_grapple import apply_multi_hit_grapples
from app.combat.source_turn_relation_damage import resolve_source_turn_relation_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_multi_hit_engulf_source_2014 import source_two_hit_engulf_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.size import CreatureSize
from scripts.browser_template_serializer import template_row


def _source():
    return next(x for x in load_monster_source_2014() if x.id == "shambling-mound")


def _fight():
    source = _source()
    definition = adapt_monster_mechanics_2014(source)
    owner = EncounterCombatant(
        combatant_id="owner", side="monsters", position_ft=0,
        state=build_combatant_state(compile_combatant(definition)),
    )
    target = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=5,
        state=build_combatant_state(
            build_demo_fighter().model_copy(update={"size": CreatureSize.MEDIUM, "max_hp": 90})
        ),
    )
    setup = EncounterSetup(
        heroes=[target], monsters=[owner], hero_total_levels=1,
        monster_total_cr="5", ruleset="2014",
    )
    return owner, target, setup


def test_source_proof_and_browser_template_are_consistent():
    source = _source()
    unchanged = source.model_dump_json()
    profile = source_two_hit_engulf_2014(source)
    assert profile is not None, (
        "Printed Engulf was not proven; raw source declaration: "
        + repr(source.swallow_actions)
        + " / multiattack: " + repr(source.multiattack_slots)
        + " / action sections: " + repr(source.source_actions[-2000:])
    )
    action, damage = profile
    assert (action.hits_required, action.escape_dc, action.max_active_grapples) == (2, 14, 1)
    assert (action.blinds, action.restrains, action.prevents_breathing) == (True, True, True)
    assert (damage.save_ability, damage.save_dc, damage.damage_bonus) == ("constitution", 14, 4)
    assert (damage.dice_count, damage.dice_size, damage.damage_type.value) == (2, 8, "bludgeoning")
    assert "mechanic:swallow" not in basic_blockers_2014(source)
    assert basic_blockers_2014(source) == ()
    monster = compile_combatant(adapt_monster_mechanics_2014(source))
    browser = template_row(monster)
    assert browser["multiHitGrappleEffects"][0]["hitsRequired"] == 2
    assert browser["multiHitGrappleEffects"][0]["attackId"] == action.attack_id
    assert browser["source_turn_relation_damages"][0]["save_dc"] == 14
    assert source.model_dump_json() == unchanged


def test_source_drift_and_renaming_do_not_invent_behavior():
    source = _source()
    profile = source_two_hit_engulf_2014(source)
    assert profile is not None
    renamed = source.model_copy(update={"id": "renamed-source", "name": "Renamed Holder"})
    renamed_rule = source_two_hit_engulf_2014(renamed)
    assert renamed_rule is not None
    assert renamed_rule[0].hits_required == profile[0].hits_required
    # A changed printed DC is source data, not an engine change.
    changed_dc = source.model_copy(update={
        "source_actions": source.source_actions.replace("escape DC 14", "escape DC 15"),
    })
    assert source_two_hit_engulf_2014(changed_dc)[0].escape_dc == 15
    for before, after in (
        ("both attacks hit", "one attack hits"),
        ("unable to breathe", "able to breathe"),
        ("2d8 + 4", "2d8 + 5"),
        ("only one creature engulfed", "two creatures engulfed"),
    ):
        assert before in source.source_actions
        drift = source.model_copy(update={
            "source_actions": source.source_actions.replace(before, after),
        })
        assert source_two_hit_engulf_2014(drift) is None


def test_two_hits_same_target_upgrade_source_grapple_and_release():
    owner, target, setup = _fight()
    attack_id = owner.state.template.multi_hit_grapple_effects[0].attack_id

    def hit(seq, target_id="target", landed=True):
        return BattleEvent(
            sequence=seq, round_number=1, event_type="attack",
            actor_id="owner", actor_name="Renamed Holder",
            target_id=target_id, attack_id=attack_id, hit=landed,
            description="Source-neutral Slam attack.", animation="attack",
        )

    for attacks in ([hit(1)], [hit(1), hit(2, landed=False)]):
        assert apply_multi_hit_grapples(3, 1, owner, setup, attacks) == ([], 3)
    results, sequence = apply_multi_hit_grapples(
        3, 1, owner, setup, [hit(1), hit(2)],
    )
    assert sequence == 4 and len(results) == 1
    assert results[0].feature_id == "Engulf"
    assert results[0].applied_condition_ids == ["grappled", "restrained", "blinded"]
    assert [x.source_id for x in target.state.grapple_sources] == ["owner"]
    assert target.state.grapple_sources[0].escape_dc == 14
    assert target.state.grapple_sources[0].prevents_breathing is True
    assert all(x in target.state.active_effect_ids for x in ("grappled", "restrained", "blinded"))

    hp = target.state.current_hp
    saved, _ = resolve_source_turn_relation_damage(
        4, 2, owner, setup, FixedDiceProvider([20]),
    )
    assert saved[0].save_succeeded is True and target.state.current_hp == hp
    failed, _ = resolve_source_turn_relation_damage(
        5, 3, owner, setup, FixedDiceProvider([1, 8, 8]),
    )
    assert failed[0].save_succeeded is False
    assert target.state.current_hp == hp - 20
    release_grapple(target.state, "owner")
    assert not any(x in target.state.active_effect_ids for x in ("grappled", "restrained", "blinded"))
    assert resolve_source_turn_relation_damage(
        6, 4, owner, setup, FixedDiceProvider([1]),
    ) == ([], 6)


def test_second_double_hit_grapples_at_engulf_capacity_then_upgrades_after_release():
    """Capacity limits linked Engulf, not the ordinary source-owned Grappled state."""
    owner, first, setup = _fight()
    second = EncounterCombatant(
        combatant_id="second", side="heroes", position_ft=5,
        state=build_combatant_state(
            build_demo_fighter().model_copy(update={"size": CreatureSize.MEDIUM, "max_hp": 90})
        ),
    )
    setup.heroes.append(second)
    attack_id = owner.state.template.multi_hit_grapple_effects[0].attack_id

    def double_hit(target_id: str) -> list[BattleEvent]:
        return [BattleEvent(
            sequence=index, round_number=1, event_type="attack",
            actor_id="owner", actor_name=owner.state.template.name,
            target_id=target_id, attack_id=attack_id, hit=True,
            description="Source-neutral landed Slam.", animation="attack",
        ) for index in (1, 2)]

    linked, _ = apply_multi_hit_grapples(3, 1, owner, setup, double_hit("target"))
    assert len(linked) == 1
    assert first.state.grapple_sources[0].linked_effect_id == "engulf"

    fallback, _ = apply_multi_hit_grapples(4, 1, owner, setup, double_hit("second"))
    assert len(fallback) == 1
    assert fallback[0].applied_condition_ids == ["grappled"]
    assert "capacity reached" in fallback[0].description
    held = second.state.grapple_sources[0]
    assert held.source_id == "owner" and held.escape_dc == 14
    assert held.linked_effect_id is None
    assert held.restrains is False and held.blinds is False
    assert held.prevents_breathing is False
    assert "restrained" not in second.state.active_effect_ids
    assert "blinded" not in second.state.active_effect_ids

    # Hitting the already engulfed target cannot erase its linked state.
    again, _ = apply_multi_hit_grapples(5, 1, owner, setup, double_hit("target"))
    assert again == []
    assert first.state.grapple_sources[0].linked_effect_id == "engulf"

    # Ordinary Grappled must never receive Engulf-only turn damage.
    saved, _ = resolve_source_turn_relation_damage(
        6, 2, owner, setup, FixedDiceProvider([20]),
    )
    assert len(saved) == 1 and saved[0].target_id == "target"

    release_grapple(first.state, "owner")
    upgraded = resolve_grapple_upgrade_action(7, 2, owner, setup)
    assert upgraded is not None and upgraded[0][0].target_id == "second"
    assert second.state.grapple_sources[0].linked_effect_id == "engulf"
    assert "blinded" in second.state.active_effect_ids
    assert "restrained" in second.state.active_effect_ids
