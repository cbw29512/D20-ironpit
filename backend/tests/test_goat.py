from app.combat.attacks import resolve_attack
from app.combat.charge import charge_profile_for_attack_id, resolve_charge_closing
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_goat import build_goat
from app.content.monster_saving_throws import with_source_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.domain.catalog import CoverageStatus
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _goat():
    return with_source_saving_throws(build_goat())


def _opening_pair():
    goat = EncounterCombatant(
        combatant_id="monster-1:srd-goat", side="monsters", position_ft=5,
        state=build_combatant_state(_goat()),
    )
    hero = EncounterCombatant(
        combatant_id="hero-1:karnok", side="heroes", position_ft=0,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    goat.state.initiative_total = 20
    hero.state.initiative_total = 10
    begin_turn(goat.state)
    return goat, hero, EncounterSetup(
        heroes=[hero], monsters=[goat], hero_total_levels=1, monster_total_cr="0",
    )


def test_goat_ram_and_charge_replacement_match_srd() -> None:
    goat = _goat()
    ram = goat.weapon_attack
    assert (ram.id, ram.attack_bonus, ram.fixed_damage) == ("goat-ram", 2, 1)
    profile = charge_profile_for_attack_id("goat-ram")
    assert profile is not None and profile.replacement_damage is not None
    assert profile.minimum_move_ft == 20
    assert profile.max_target_size is None
    assert profile.prone_max_target_size is None
    assert profile.bonus_damage is None
    replacement = profile.replacement_damage
    assert (replacement.dice_count, replacement.dice_size, replacement.damage_bonus) == (1, 4, 0)
    assert replacement.damage_type.value == "bludgeoning"
    row = next(row for row in load_monster_rows() if row["name"] == "Goat")
    assert audit_monster_source(goat, row) == []


def test_goat_normal_ram_is_fixed_one_damage() -> None:
    goat = build_combatant_state(_goat())
    target = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    event = resolve_attack(
        1, 1, goat, target, goat.template.weapon_attack, 5,
        FixedDiceProvider([19]), actor_event_id="goat", target_event_id="target", spend_action=False,
    )
    assert event.hit is True
    assert event.damage_roll is not None and event.damage_roll.notation == "1"
    assert event.damage_roll.total == 1


def test_goat_opening_charge_replaces_fixed_damage_without_prone() -> None:
    goat, target, setup = _opening_pair()
    events, sequence, handled = resolve_charge_closing(
        1, 1, goat, target, FixedDiceProvider([19, 3]), setup,
    )
    attacks = [event for event in events if event.event_type == "attack"]
    assert handled is True and sequence == 2
    assert len(attacks) == 1
    event = attacks[0]
    assert event.hit is True and event.feature_id == "charge"
    assert event.damage_roll is not None and event.damage_roll.notation == "1d4+0"
    assert event.damage_roll.total == 3
    assert "prone" not in event.applied_condition_ids


def test_goat_is_raw_ready() -> None:
    card = next(card for card in build_monster_catalog() if card.name == "Goat")
    assert card.coverage_status is CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-goat"
    assert card.blockers == []
