from app.combat.dice import FixedDiceProvider
from app.combat.encounter_initiative import roll_encounter_initiative
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.barbarian_progression import build_rokhan_stonefury_level7_candidate
from app.content.certified_heroes import build_certified_hero_registry
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode


def _member(template, combatant_id: str, side: str) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=0 if side == "heroes" else 60,
        state=build_combatant_state(template),
    )


def test_barbarian_seven_has_deterministic_raw_progression_and_public_certification() -> None:
    template = build_rokhan_stonefury_level7_candidate()
    assert (template.id, template.level, template.max_hp, template.armor_class, template.speed_ft) == (
        "rokhan-stonefury-l7", 7, 75, 14, 40,
    )
    assert {item.id: item.max_uses for item in template.resources} == {
        "rage": 4, "adrenaline-rush": 3, "relentless-endurance": 1,
    }
    features = template.progression_features
    assert features.initiative_advantage is True
    assert features.instinctive_pounce_fraction == 0.0
    assert features.mindless_rage is True
    assert features.fast_movement_bonus_ft == 10
    assert features.frenzy is True and features.reckless_attack is True and features.danger_sense is True
    assert build_certified_hero_registry()[("barbarian", 7, "canonical")] == (
        "Rokhan Stonefury", "rokhan-stonefury-l7",
    )


def test_feral_instinct_reuses_shared_initiative_advantage_while_pounce_is_arena_neutral() -> None:
    rokhan = _member(build_rokhan_stonefury_level7_candidate(), "rokhan", "heroes")
    opponent = _member(build_karnok_stoneward(), "opponent", "monsters")
    setup = EncounterSetup(
        heroes=[rokhan], monsters=[opponent], hero_total_levels=7, monster_total_cr="1",
    )
    initiative = roll_encounter_initiative(setup, FixedDiceProvider([2, 18, 10]))
    hero_group = next(group for group in initiative.groups if group.side == "heroes")
    assert hero_group.initiative_roll.mode is RollMode.ADVANTAGE
    assert hero_group.initiative_roll.selected_roll == 18
    assert hero_group.initiative_count == 19
