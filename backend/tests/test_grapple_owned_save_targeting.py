"""Universal source-owned grapple relation for named or renamed save Actions."""
from __future__ import annotations

import pytest

from app.combat.grapple import apply_grapple, release_grapple
from app.combat.multi_target_save_actions import choose_multi_target_save_action
from app.combat.saving_throw_legality import legal_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import _compile_save
from app.content.monsters import build_commoner
from app.domain.capability_save_definitions import SaveCapabilityDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup


def member(identifier: str, side: str) -> EncounterCombatant:
    try:
        return EncounterCombatant(
            combatant_id=identifier, side=side, position_ft=5,
            state=build_combatant_state(build_commoner()),
        )
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to construct %s", identifier)
        raise


def test_grapple_source_targeting_and_ally_scope() -> None:
    actor = member("source", "monsters")
    friend = member("friend", "monsters")
    held = member("held", "heroes")
    other = member("other", "heroes")
    unrelated = member("unrelated", "heroes")
    apply_grapple(held.state, actor.combatant_id, 13, 10, restrains=True)
    apply_grapple(friend.state, actor.combatant_id, 13, 10)
    apply_grapple(unrelated.state, "other-source", 13, 10)
    definition = SaveCapabilityDefinition(
        id="synthetic-held-save", name="Arbitrary Grapple Pulse",
        save_ability="constitution", dc=14, range_ft=10,
        max_targets=2, target_scope="all-other-creatures",
        requires_target_grappled_by_source=True,
    )
    action = _compile_save(definition)
    actor.state.template.saving_throw_actions = [action]
    setup = EncounterSetup(
        heroes=[held, other, unrelated], monsters=[actor, friend],
        hero_total_levels=3, monster_total_cr="2", ruleset="2014",
    )
    assert legal_save_action(action, held, 5, source_id="source", actor=actor)
    assert legal_save_action(action, friend, 5, source_id="source", actor=actor)
    assert not legal_save_action(action, unrelated, 5, source_id="source", actor=actor)
    assert not legal_save_action(action, other, 5, source_id="source", actor=actor)
    assert not legal_save_action(action, held, 5, source_id="someone-else", actor=actor)
    picked = choose_multi_target_save_action(actor, setup)
    assert picked is not None and picked[0].id == action.id
    assert {x.combatant_id for x in picked[1]} == {"held", "friend"}
    assert actor.state.action_available
    release_grapple(held.state, actor.combatant_id)
    assert not legal_save_action(action, held, 5, source_id="source", actor=actor)
    assert [x.combatant_id for x in choose_multi_target_save_action(actor, setup)[1]] == ["friend"]
    release_grapple(friend.state, actor.combatant_id)
    assert choose_multi_target_save_action(actor, setup) is None
    assert actor.state.action_available


def test_renamed_ability_and_unrestricted_save_compatibility() -> None:
    original = SaveCapabilityDefinition(
        id="generic", name="Something", save_ability="constitution",
        dc=14, range_ft=10, max_targets=2,
        requires_target_grappled_by_source=True,
    )
    renamed = original.model_copy(update={"name": "Totally Different Label"})
    assert _compile_save(original).requires_target_grappled_by_source
    assert _compile_save(renamed).requires_target_grappled_by_source
    assert not _compile_save(SaveCapabilityDefinition(
        id="legacy", name="Ordinary Save", save_ability="wisdom", dc=12, range_ft=5,
    )).requires_target_grappled_by_source
    with pytest.raises(ValueError):
        SaveCapabilityDefinition.model_validate({**original.model_dump(), "max_targets": 0})
