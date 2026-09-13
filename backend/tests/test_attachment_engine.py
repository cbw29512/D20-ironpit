from app.combat.attachments import detach_source_by_movement, resolve_attachment_start_turn, resolve_detach_action
from app.combat.attack_legality import attack_available_for_source
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _row(name: str):
    return next(row for row in load_monster_rows() if row["name"] == name)


def _setup():
    stirge_template = build_combatant_from_capabilities("srd-stirge")
    hero_template = build_karnok_stoneward()
    stirge = EncounterCombatant(
        combatant_id="stirge", side="monsters", position_ft=5,
        state=build_combatant_state(stirge_template),
    )
    hero = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=0,
        state=build_combatant_state(hero_template),
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[stirge], hero_total_levels=hero_template.level or 1,
        monster_total_cr="1/8",
    )
    return stirge, hero, setup


def test_stirge_compiles_and_source_audits_through_attachment_primitive() -> None:
    stirge = build_combatant_from_capabilities("srd-stirge")
    rule = stirge.weapon_attack.attachment_on_hit
    assert rule is not None
    assert (rule.periodic_damage_count, rule.periodic_damage_size, rule.periodic_damage_type.value) == (2, 4, "necrotic")
    assert rule.detachable_by_source_movement_ft == 5
    assert stirge.weapon_attack.id in rule.forbids_source_attack_ids
    assert audit_monster_source(stirge, _row("Stirge")) == []


def test_attachment_hit_locks_attack_and_ticks_through_normal_damage_pipeline() -> None:
    stirge, hero, setup = _setup()
    attack = stirge.state.template.weapon_attack
    resolve_attack(
        1, 1, stirge.state, hero.state, attack, 5, FixedDiceProvider([15, 3]),
        actor_event_id="stirge", target_event_id="hero", spend_action=False,
    )
    assert stirge.state.attachment is not None
    assert stirge.state.attachment.target_id == "hero"
    assert attack_available_for_source(attack, stirge.state) is False

    events, sequence = resolve_attachment_start_turn(2, 2, stirge, setup, FixedDiceProvider([4, 3]))
    assert sequence == 3
    assert len(events) == 1
    assert events[0].damage_roll is not None and events[0].damage_roll.total == 7
    assert hero.state.current_hp == 1
    assert next(item for item in hero.state.resources if item.id == "relentless-endurance").current_uses == 0


def test_target_action_and_source_movement_can_detach() -> None:
    stirge, hero, setup = _setup()
    attack = stirge.state.template.weapon_attack
    resolve_attack(
        1, 1, stirge.state, hero.state, attack, 5, FixedDiceProvider([15, 2]),
        actor_event_id="stirge", target_event_id="hero", spend_action=False,
    )
    event = resolve_detach_action(2, 1, hero, setup)
    assert event is not None
    assert hero.state.action_available is False
    assert stirge.state.attachment is None

    hero.state.action_available = True
    resolve_attack(
        3, 2, stirge.state, hero.state, attack, 5, FixedDiceProvider([15, 2]),
        actor_event_id="stirge", target_event_id="hero", spend_action=False,
    )
    stirge.state.movement_remaining_ft = 40
    assert detach_source_by_movement(stirge.state) == 5
    assert stirge.state.movement_remaining_ft == 35
    assert stirge.state.attachment is None
