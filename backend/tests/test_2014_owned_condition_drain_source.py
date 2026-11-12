"""2014 source proof for Iron Pit Draining Kiss: source-owned Charm only."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.content.capability_compiler import _compile_save
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_owned_condition_drain_2014 import (
    source_proven_owned_condition_drains_2014,
)
from app.domain.actions import SavingThrowAction
from app.domain.capability_save_definitions import SaveCapabilityDefinition

logger = logging.getLogger(__name__)
_scripts = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from browser_template_serializer import _save


def _source():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        matching = [c for c in cards if source_proven_owned_condition_drains_2014(c)]
        assert len(matching) == 1, "New members require a source audit of every printed clause."
        return matching[0]
    except Exception:
        logger.exception("Failed to identify the full 2014 owned-condition drain family.")
        raise


def test_2014_source_draining_save_is_compiled_without_inventing_control():
    try:
        source = _source()
        immutable = source.model_dump_json()
        (action,) = source_proven_owned_condition_drains_2014(source)
        assert (action.id, action.name) == ("draining-kiss", "Draining Kiss")
        assert (action.dc, action.save_ability, action.range_ft) == (15, "constitution", 5)
        assert (action.damage.count, action.damage.size, action.damage.bonus) == (5, 10, 5)
        assert action.damage_type.value == "psychic"
        assert action.success_damage == "half" and action.magical_effect
        assert action.required_target_source_condition is None
        assert action.target_scope == "enemies"
        assert action.target_qualification.any_of == ["source_charmed"]
        assert action.reduce_hit_point_maximum_on_damage and action.max_hp_zero_kills
        assert any(item.id == action.id for item in save_capabilities_2014(source))
        runtime = _compile_save(action)
        assert runtime.required_target_source_condition is None
        assert runtime.target_scope == "enemies"
        assert runtime.target_qualification.any_of == ["source_charmed"]
        assert runtime.reduce_hit_point_maximum_on_damage
        assert runtime.max_hp_zero_kills
        browser = _save(runtime)
        assert browser["targetScope"] == "enemies"
        assert browser["targetQualification"]["anyOf"] == ["source_charmed"]
        assert "requiredTargetSourceCondition" not in browser
        assert browser["reduceHitPointMaximumOnDamage"] is True
        assert browser["maxHpZeroKills"] is True
        # The arena forbids voluntary targets; Charm command obedience remains blocked.
        assert "source:extra-action" in basic_blockers_2014(source)
        assert source.model_dump_json() == immutable
        renamed = source.model_copy(update={"id": "renamed-source", "name": "Unknown"})
        assert source_proven_owned_condition_drains_2014(renamed) == [action]
    except Exception:
        logger.exception("Source-proven owned-condition drain binding failed.")
        raise


@pytest.mark.parametrize("before,after", [
    ("a creature charmed by it", "a creature frightened by it"),
    ("a willing creature", "any creature"),
    ("DC 15 Constitution", "DC 19 Wisdom"),
    ("5d10 + 5", "6d10 + 5"),
    ("half as much damage", "no damage"),
    ("amount equal to the damage taken", "twice the damage taken"),
    ("target finishes a long rest", "target takes a short rest"),
    ("hit point maximum to 0", "hit point maximum to 1"),
])
def test_printed_source_mutations_fail_closed(before, after):
    try:
        source = _source()
        assert before in source.source_actions
        mutated = source.model_copy(update={
            "source_actions": source.source_actions.replace(before, after),
        })
        assert source_proven_owned_condition_drains_2014(mutated) == []
    except Exception:
        logger.exception("Owned-condition drain source mutation failed: %s.", before)
        raise


def test_conflicting_source_condition_schema_fails_closed():
    try:
        with pytest.raises(ValidationError):
            SaveCapabilityDefinition(
                id="bad", name="Conflicting", save_ability="wisdom", dc=12,
                range_ft=5, required_target_condition="frightened",
                required_target_source_condition="charmed",
            )
        with pytest.raises(ValidationError):
            SavingThrowAction(
                id="bad", name="Conflicting", save_ability="wisdom", dc=12,
                range_ft=5, required_target_condition="frightened",
                required_target_source_condition="charmed",
            )
    except Exception:
        logger.exception("Owned-condition schema validation failed.")
        raise
