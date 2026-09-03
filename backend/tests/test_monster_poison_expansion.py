from app.combat.condition_lifecycle import resolve_source_condition_timing, resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.monsters_poison import build_giant_vulture, build_wyvern
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.traits import CombatTrait


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def _runtime(name: str):
    return next(template for template in build_arena_roster().monsters if template.name == name)


def _member(template, combatant_id: str, side: str, position: int):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_poison_expansion_reconciles_exact_srd_riders() -> None:
    for name in ("Giant Vulture", "Wyvern"):
        assert audit_monster_source(_runtime(name), _row(name)) == []


def test_source_audit_rejects_wrong_poison_turn_timing() -> None:
    vulture = _runtime("Giant Vulture").model_copy(deep=True)
    vulture.weapon_attack.control_effect.expiry_timing = "source_turn_start"
    assert "condition-rider-mismatch:giant-vulture-gouge:poisoned" in audit_monster_source(vulture, _row("Giant Vulture"))


def test_giant_vulture_profile_and_target_turn_end_poison() -> None:
    vulture = build_giant_vulture()
    assert (vulture.armor_class, vulture.max_hp, vulture.speed_ft, vulture.initiative_bonus) == (10, 25, 60, 0)
    assert CombatTrait.PACK_TACTICS in vulture.combat_traits
    assert [item.value for item in vulture.damage_resistances] == ["necrotic"]
    attack = vulture.weapon_attack
    assert (attack.attack_bonus, attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (4, 2, 6, 2)
    assert attack.control_effect is not None
    assert (attack.control_effect.condition_id, attack.control_effect.expiry_timing) == ("poisoned", "target_turn_end")

    source = _member(vulture, "monster-1:vulture", "monsters", 5)
    target = _member(build_karnok_stoneward(), "hero-1:karnok", "heroes", 0)
    setup = EncounterSetup(heroes=[target], monsters=[source], hero_total_levels=1, monster_total_cr="1")
    event = resolve_encounter_attack(1, 1, source, target, attack, 5, FixedDiceProvider([15, 4, 4]), setup)
    assert event.hit is True and "poisoned" in event.applied_condition_ids
    ended, _ = resolve_target_condition_timing(2, 1, target, "target_turn_end", FixedDiceProvider([10]))
    assert len(ended) == 1 and ended[0].removed_condition_ids == ["poisoned"]


def test_wyvern_sting_damage_multiattack_and_source_turn_start_poison() -> None:
    wyvern = build_wyvern()
    assert (wyvern.armor_class, wyvern.max_hp, wyvern.speed_ft, wyvern.initiative_bonus) == (14, 127, 80, 0)
    bite, sting = wyvern.weapon_attack, wyvern.alternate_weapon_attacks[0]
    assert [slot.attack_ids for slot in wyvern.attack_action.slots] == [[bite.id], [sting.id]]
    assert (sting.weapon.reach_ft, sting.weapon.dice_count, sting.weapon.dice_size, sting.damage_bonus) == (10, 2, 6, 4)
    assert (sting.on_hit_damage[0].dice_count, sting.on_hit_damage[0].dice_size, sting.on_hit_damage[0].damage_type.value) == (7, 6, "poison")
    assert sting.control_effect is not None
    assert (sting.control_effect.condition_id, sting.control_effect.expiry_timing) == ("poisoned", "source_turn_start")

    source = _member(wyvern, "monster-1:wyvern", "monsters", 10)
    target = _member(build_karnok_stoneward(), "hero-1:karnok", "heroes", 0)
    setup = EncounterSetup(heroes=[target], monsters=[source], hero_total_levels=1, monster_total_cr="6")
    event = resolve_encounter_attack(
        1, 1, source, target, sting, 10,
        FixedDiceProvider([15, 2, 2, 1, 1, 1, 1, 1, 1, 1]), setup,
    )
    assert event.hit is True and "poisoned" in event.applied_condition_ids
    ended, _ = resolve_source_condition_timing(2, 2, source, setup, "source_turn_start")
    assert len(ended) == 1 and ended[0].removed_condition_ids == ["poisoned"]


def test_poison_expansion_is_raw_ready() -> None:
    cards = {card.name: card for card in build_monster_catalog()}
    for name in ("Giant Vulture", "Wyvern"):
        assert cards[name].coverage_status is CoverageStatus.RAW_READY
        assert cards[name].runnable_template_id is not None
        assert cards[name].blockers == []
