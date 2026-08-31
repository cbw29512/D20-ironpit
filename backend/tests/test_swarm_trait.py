from app.combat.encounter_setup import build_encounter_setup
from app.combat.healing import choose_healing_target
from app.combat.state import build_combatant_state
from app.combat.temporary_hp import grant_temporary_hit_points
from app.combat.zero_hp import restore_hit_points
from app.content.monster_catalog import load_monster_rows
from app.content.monster_trait_source_audit import trait_issues
from app.content.monsters_low_cr import build_giant_rat
from app.domain.models import EncounterSelection, HealingAction
from app.domain.traits import CombatTrait


def _swarm_state():
    template = build_giant_rat().model_copy(deep=True)
    template.combat_traits = [CombatTrait.SWARM]
    return build_combatant_state(template)


def test_swarm_cannot_regain_hit_points() -> None:
    state = _swarm_state()
    state.current_hp = 1
    assert restore_hit_points(state, 20) == 0
    assert state.current_hp == 1


def test_swarm_cannot_gain_temporary_hit_points() -> None:
    state = _swarm_state()
    assert grant_temporary_hit_points(state, 7) == 0
    assert state.temporary_hp == 0


def test_healing_policy_never_selects_a_swarm() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["aldric-vane-l1", "brom-ironmark-l1"],
        monster_ids=["srd-goblin-warrior"], starting_distance_ft=30,
    ))
    healer, target = setup.heroes
    target.state.template.combat_traits.append(CombatTrait.SWARM)
    target.state.current_hp = 1
    action = HealingAction(
        id="test-heal", name="Test Heal", action_cost="action", range_ft=60,
        target_mode="ally", healing_bonus=5,
    )
    assert choose_healing_target(healer, setup, action) is None


def test_real_srd_swarm_trait_matches_runtime_semantics() -> None:
    row = next(row for row in load_monster_rows() if row["name"] == "Swarm of Bats")
    template = build_giant_rat().model_copy(update={
        "source_trait_names": ["Swarm"],
        "combat_traits": [CombatTrait.SWARM],
    })
    assert trait_issues(template, row) == []
