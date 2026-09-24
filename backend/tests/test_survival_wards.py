from app.combat.defensive_spell_resolution import resolve_defensive_spell
from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage, apply_instant_death
from app.content.fighter_progression import build_karnok_stoneward_level
from app.domain.encounters import EncounterCombatant
from app.domain.models import ResourceState
from app.domain.spells import DefensiveSpellAction
from app.domain.zero_hp_effects import SurvivalWard


def _member() -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id="target",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(build_karnok_stoneward_level(1)),
    )


def _apply(member: EncounterCombatant) -> None:
    spell = DefensiveSpellAction(
        id="test-survival-ward",
        name="Test Survival Ward",
        level=4,
        range_ft=5,
        duration_minutes=480,
        target_policy="friendly",
        survival_ward=SurvivalWard(replacement_hp=1, prevents_nondamage_instant_death=True),
    )
    resource = ResourceState(id="spell-slot-4", name="Level 4 Spell Slot", current_uses=1, max_uses=1)
    resolve_defensive_spell(1, member, [member], spell, 4, resource)


def test_survival_ward_prevents_zero_hp_before_innate_recovery() -> None:
    member = _member()
    _apply(member)
    relentless = next(item for item in member.state.resources if item.id == "relentless-endurance")
    outcome = apply_damage(member.state, member.state.current_hp + member.state.template.max_hp)
    assert outcome == "survival_ward"
    assert member.state.current_hp == 1
    assert relentless.current_uses == 1
    assert "Test Survival Ward" in " ".join(member.state.pending_survival_save_logs)


def test_survival_ward_negates_nondamage_instant_death_once() -> None:
    member = _member()
    _apply(member)
    assert apply_instant_death(member.state) == "survival_ward"
    assert member.state.current_hp == 1
    assert member.state.is_dead is False
    assert apply_instant_death(member.state) == "dead"
