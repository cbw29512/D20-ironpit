"""Iron Pit: no planar removal; Hurl Through Hell is a timed protection and delayed hit."""
from app.combat.damage_defenses import resolve_damage_amount
from app.combat.dice import FixedDiceProvider
from app.combat.exile import apply_on_hit_exile, removed_from_battlefield, resolve_source_exile_returns
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.warlock_fiend_2024_runtime import build_varek_ashenmark_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType


def test_2024_hurl_uses_deferred_eight_d10_with_save_and_no_banishment():
    hero = build_varek_ashenmark_2024(14)
    target = build_commoner().model_copy(update={"ruleset": "2024", "max_hp": 200})
    source = EncounterCombatant(
        combatant_id="caster", side="heroes", position_ft=0, state=build_combatant_state(hero),
    )
    victim = EncounterCombatant(
        combatant_id="victim", side="monsters", position_ft=5, state=build_combatant_state(target),
    )
    encounter = EncounterSetup(
        heroes=[source], monsters=[victim], hero_total_levels=14,
        monster_total_cr="0", ruleset="2024",
    )
    outcome = apply_on_hit_exile(
        source.state, victim.state, None, attacker_id="caster",
        round_number=1, affected_states=[source.state, victim.state],
        dice=FixedDiceProvider([1]), turn_key="1:caster",
    )
    assert outcome == ("hurl-through-hell", 0)
    assert not removed_from_battlefield(victim.state)
    assert victim.state.current_hp == 200
    assert "hurl-through-hell" in victim.state.active_effect_ids
    assert "incapacitated" in victim.state.active_effect_ids
    assert resolve_damage_amount(30, DamageType.FIRE, victim.state)[0] == 0
    assert resolve_damage_amount(30, DamageType.PSYCHIC, victim.state)[0] == 0

    events, _ = resolve_source_exile_returns(
        1, 1, source, encounter, FixedDiceProvider([5] * 8),
    )
    assert not events  # One full source-turn cycle; no early expiry.
    events, _ = resolve_source_exile_returns(
        1, 2, source, encounter, FixedDiceProvider([5] * 8),
    )
    assert len(events) == 1
    assert events[0].feature_id == "hurl-through-hell"
    assert events[0].damage_roll.total == 40
    assert victim.state.current_hp == 160
    assert "hurl-through-hell" not in victim.state.active_effect_ids
    assert "incapacitated" not in victim.state.active_effect_ids
    assert not any(effect.all_damage_immunity for effect in victim.state.timed_effects)
    assert not removed_from_battlefield(victim.state)
