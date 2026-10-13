from __future__ import annotations

from app.combat.state import build_combatant_state
from app.combat.turn_start_reaction_eligibility import eligible_turn_start_reaction
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant
from app.domain.turn_start_save_reaction import TurnStartSaveReaction


def _combatant(name: str, side: str, position: int, *, source: bool = False):
    template = build_kael_stillwater_2024(3)
    if source:
        template = template.model_copy(update={
            "turn_start_save_reaction": TurnStartSaveReaction(
                source_id="turn-start-fear", source_name="Turn-start Fear",
                range_ft=30, save_ability="wisdom", save_dc=14,
            ),
        })
    return EncounterCombatant(
        combatant_id=name, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_eligible_enemy_at_30_feet_and_no_friendly_fire() -> None:
    source = _combatant("source", "monsters", 0, source=True)
    foe = _combatant("foe", "heroes", 30)
    ally = _combatant("ally", "monsters", 30)
    assert eligible_turn_start_reaction(source, foe)
    assert not eligible_turn_start_reaction(source, ally)
    assert not eligible_turn_start_reaction(source, source)


def test_reaction_range_and_resource_are_enforced() -> None:
    source = _combatant("source", "monsters", 0, source=True)
    far = _combatant("far", "heroes", 35)
    near = _combatant("near", "heroes", 5)
    assert not eligible_turn_start_reaction(source, far)
    source.state.reaction_available = False
    assert not eligible_turn_start_reaction(source, near)


def test_missing_reaction_rule_is_ineligible() -> None:
    source = _combatant("source", "monsters", 0)
    foe = _combatant("foe", "heroes", 5)
    assert not eligible_turn_start_reaction(source, foe)


def test_directional_visibility_and_measured_range(monkeypatch) -> None:
    import app.combat.turn_start_reaction_eligibility as eligibility

    source = _combatant("source", "monsters", 0, source=True)
    foe = _combatant("foe", "heroes", 30)
    seen = []

    def visibility(observer, target, distance_ft):
        seen.append((observer is source.state, distance_ft))
        return observer is source.state

    monkeypatch.setattr(eligibility, "can_see", visibility)
    assert not eligible_turn_start_reaction(source, foe)
    assert seen == [(True, 30), (False, 30)]


def test_source_must_see_target_before_reaction(monkeypatch) -> None:
    import app.combat.turn_start_reaction_eligibility as eligibility

    source = _combatant("source", "monsters", 0, source=True)
    foe = _combatant("foe", "heroes", 5)
    monkeypatch.setattr(eligibility, "can_see", lambda *_args: False)
    assert not eligible_turn_start_reaction(source, foe)
    assert source.state.reaction_available is True
