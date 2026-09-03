from app.combat.attacks import resolve_attack
from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import effective_speed
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_merfolk_skirmisher import build_merfolk_skirmisher
from app.content.monster_saving_throws import with_source_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_trait_source_audit import complete_monster_trait_fingerprints
from app.domain.catalog import CoverageStatus
from app.domain.encounters import EncounterCombatant
from app.domain.modifiers import ModifierKind
from app.domain.models import WeaponAttackKind


def _merfolk():
    template = complete_monster_trait_fingerprints([build_merfolk_skirmisher()])[0]
    return with_source_saving_throws(template)


def test_merfolk_ocean_spear_matches_srd_source() -> None:
    merfolk = _merfolk()
    ranged, melee = merfolk.weapon_attack, merfolk.alternate_weapon_attacks[0]
    assert merfolk.creature_type == "elemental"
    assert ranged.weapon.attack_kind is WeaponAttackKind.RANGED
    assert melee.weapon.attack_kind is WeaponAttackKind.MELEE
    assert (ranged.weapon.normal_range_ft, ranged.weapon.long_range_ft) == (20, 60)
    assert melee.weapon.reach_ft == 5
    for attack in (ranged, melee):
        assert (attack.attack_bonus, attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (2, 1, 6, 0)
        assert [(part.dice_count, part.dice_size, part.damage_type.value) for part in attack.on_hit_damage] == [(1, 4, "cold")]
        assert len(attack.on_hit_modifier_effects) == 1
        slow = attack.on_hit_modifier_effects[0]
        assert slow.kind == "speed" and slow.flat_bonus == -10
        assert slow.expires_at_end_of_target_turn is True
    assert merfolk.movement_modes.walk_ft == 10 and merfolk.movement_modes.swim_ft == 40
    assert merfolk.source_trait_names == ["Amphibious"]
    row = next(row for row in load_monster_rows() if row["name"] == "Merfolk Skirmisher")
    assert audit_monster_source(merfolk, row) == []


def test_merfolk_hit_slows_until_end_of_target_next_turn() -> None:
    merfolk = build_combatant_state(_merfolk())
    target = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    event = resolve_attack(
        1, 1, merfolk, target, merfolk.template.weapon_attack, 20,
        FixedDiceProvider([15, 1, 1]), actor_event_id="merfolk", target_event_id="target", spend_action=False,
    )
    assert event.hit is True
    assert event.damage_roll is not None and event.damage_roll.notation == "1d6+0 + 1d4+0"
    assert len(target.active_modifiers) == 1
    slow = target.active_modifiers[0]
    assert slow.kind is ModifierKind.SPEED and slow.flat_bonus == -10
    assert slow.expires_at_end_of_target_turn is True
    assert effective_speed(target) == 20
    begin_turn(target)
    assert target.movement_remaining_ft == 20

    member = EncounterCombatant(combatant_id="target", side="heroes", position_ft=0, state=target)
    events, sequence = resolve_target_condition_timing(
        2, 1, member, "target_turn_end", FixedDiceProvider([]),
    )
    assert events == [] and sequence == 2
    assert target.active_modifiers == []
    assert effective_speed(target) == 30


def test_merfolk_miss_does_not_apply_speed_modifier() -> None:
    merfolk = build_combatant_state(_merfolk())
    target = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    target.template.armor_class = 30
    event = resolve_attack(
        1, 1, merfolk, target, merfolk.template.weapon_attack, 20,
        FixedDiceProvider([1]), actor_event_id="merfolk", target_event_id="target", spend_action=False,
    )
    assert event.hit is False
    assert target.active_modifiers == []


def test_merfolk_skirmisher_is_raw_ready() -> None:
    card = next(card for card in build_monster_catalog() if card.name == "Merfolk Skirmisher")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-merfolk-skirmisher"
    assert card.blockers == []
