from app.combat.charge import charge_profile_for_attack_id, resolve_charge_closing
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.monsters_charge_expansion import build_warhorse_skeleton
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.traits import CombatTrait


def _monster(name: str):
    return next(item for item in build_arena_roster().monsters if item.name == name)


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_charge_expansion_reconciles_to_srd_source() -> None:
    for name in ("Minotaur Skeleton", "Triceratops", "Warhorse Skeleton"):
        assert audit_monster_source(_monster(name), _row(name)) == []


def test_minotaur_skeleton_charge_profile_matches_source() -> None:
    monster = _monster("Minotaur Skeleton")
    assert CombatTrait.CHARGE in monster.combat_traits
    assert [attack.id for attack in [monster.weapon_attack, *monster.alternate_weapon_attacks]] == [
        "minotaur-skeleton-gore", "minotaur-skeleton-slam",
    ]
    profile = charge_profile_for_attack_id("minotaur-skeleton-gore")
    assert profile is not None and profile.bonus_damage is not None
    assert profile.minimum_move_ft == 20
    assert (profile.bonus_damage.dice_count, profile.bonus_damage.dice_size) == (2, 8)
    assert profile.bonus_damage.damage_type.value == "piercing"
    assert profile.max_target_size.value == "large"


def test_triceratops_charge_and_multiattack_match_source() -> None:
    monster = _monster("Triceratops")
    assert CombatTrait.CHARGE in monster.combat_traits
    assert [slot.attack_ids for slot in monster.attack_action.slots] == [
        ["triceratops-gore"], ["triceratops-gore"],
    ]
    profile = charge_profile_for_attack_id("triceratops-gore")
    assert profile is not None and profile.bonus_damage is not None
    assert profile.minimum_move_ft == 20
    assert (profile.bonus_damage.dice_count, profile.bonus_damage.dice_size) == (2, 8)
    assert profile.bonus_damage.damage_type.value == "piercing"
    assert profile.max_target_size.value == "huge"


def test_warhorse_skeleton_charge_is_prone_only() -> None:
    profile = charge_profile_for_attack_id("warhorse-skeleton-hooves")
    assert profile is not None
    assert profile.minimum_move_ft == 20
    assert profile.max_target_size.value == "large"
    assert profile.bonus_damage is None

    attacker = EncounterCombatant(
        combatant_id="monster-1:warhorse-skeleton",
        side="monsters",
        position_ft=5,
        state=build_combatant_state(build_warhorse_skeleton()),
    )
    target = EncounterCombatant(
        combatant_id="hero-1:karnok",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    attacker.state.initiative_total = 20
    target.state.initiative_total = 10
    begin_turn(attacker.state)
    setup = EncounterSetup(
        heroes=[target], monsters=[attacker], hero_total_levels=1, monster_total_cr="1/2",
    )

    events, _, handled = resolve_charge_closing(
        1, 1, attacker, target, FixedDiceProvider([15, 1]), setup,
    )
    assert handled is True
    attack = events[-1]
    assert attack.feature_id == "charge"
    assert attack.damage_roll is not None and attack.damage_roll.notation == "1d6+4"
    assert "prone" in attack.applied_condition_ids


def test_charge_expansion_is_raw_ready() -> None:
    cards = {card.name: card for card in build_monster_catalog()}
    for name in ("Minotaur Skeleton", "Triceratops", "Warhorse Skeleton"):
        assert cards[name].coverage_status is CoverageStatus.RAW_READY
        assert cards[name].runnable_template_id is not None
        assert cards[name].blockers == []
