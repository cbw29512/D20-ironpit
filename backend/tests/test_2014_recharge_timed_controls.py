"""2014 Recharge timed-control source binding and shared lifecycle parity."""
from __future__ import annotations

import sys
from pathlib import Path

from app.combat.condition_lifecycle import resolve_target_condition_timing
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.start_of_turn_save_condition_events import (
    resolve_start_of_turn_save_condition_damage_events,
)
from app.content.capability_compiler import _compile_save
from app.content.monster_save_capabilities_2014 import (
    save_capabilities_2014,
    save_resources_2014,
    supports_recharge_rules_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_recharge_timed_controls_2014 import (
    source_proven_recharge_timed_controls_2014,
)
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.models import EncounterSelection
from app.combat.encounter_setup import build_encounter_setup

_scripts = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from browser_template_serializer import _save


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def _binding(monster_id: str):
    source = _source(monster_id)
    bindings = source_proven_recharge_timed_controls_2014(source)
    assert len(bindings) == 1, source_sections_2014(source.source_actions, include_continuations=True)
    return bindings[0]


def test_dust_mephit_blinding_breath_is_exact_source_owned_recharge_control() -> None:
    source, action = _source("dust-mephit"), _binding("dust-mephit")
    assert (action.id, action.name, action.save_ability, action.dc) == (
        "blinding-breath", "Blinding Breath", "dexterity", 10,
    )
    assert action.target_scope == "all-other-creatures"
    assert action.area.model_dump(exclude_none=True) == {
        "shape": "cone", "origin": "self", "length_ft": 15,
    }
    rider = action.failed_save_timed_effect
    assert rider is not None
    assert (rider.effect_id, rider.duration_rounds) == ("blinded", 10)
    assert (rider.repeat_save_ability, rider.repeat_save_dc, rider.repeat_save_timing) == (
        "dexterity", 10, "target_turn_end",
    )
    assert supports_recharge_rules_2014(source)
    assert [(item.id, item.max_uses) for item in save_resources_2014(source)] == [
        ("blinding-breath", 1),
    ]


def test_vrock_spores_bind_indefinite_poison_repeat_save_and_start_turn_damage() -> None:
    source, action = _source("vrock"), _binding("vrock")
    assert (action.id, action.name, action.save_ability, action.dc) == (
        "spores", "Spores", "constitution", 14,
    )
    assert action.area.model_dump(exclude_none=True) == {
        "shape": "emanation", "origin": "self", "radius_ft": 15,
    }
    rider = action.failed_save_timed_effect
    assert rider is not None and rider.effect_id == "poisoned"
    assert rider.expiry_timing is None and rider.duration_rounds is None
    assert (rider.repeat_save_ability, rider.repeat_save_dc, rider.repeat_save_timing) == (
        "constitution", 14, "target_turn_end",
    )
    assert (rider.start_of_turn_damage_dice_count, rider.start_of_turn_damage_dice_size) == (1, 10)
    assert str(rider.start_of_turn_damage_type) == "poison"
    assert rider.allowed_removal_action_ids == ["holy-water"]
    assert supports_recharge_rules_2014(source)


def test_vrock_browser_serialization_preserves_periodic_damage_and_no_expiry() -> None:
    card = next(item for item in save_capabilities_2014(_source("vrock")) if item.id == "spores")
    browser = _save(_compile_save(card))
    rider = browser["failedSaveTimedEffect"]
    assert rider["expiryTiming"] is None
    assert rider["repeatSaveTiming"] == "target_turn_end"
    assert rider["startOfTurnDamageDiceCount"] == 1
    assert rider["startOfTurnDamageDiceSize"] == 10
    assert rider["startOfTurnDamageType"] == "poison"
    assert rider["allowedRemovalActionIds"] == ["holy-water"]


def test_vrock_shared_failed_save_lifecycle_ticks_then_successfully_recovers() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    actor, target = setup.monsters[0], setup.heroes[0]
    action = _compile_save(_binding("vrock"))
    event = resolve_save_action(
        1, 1, actor, target, action, 5, FixedDiceProvider([1]),
        spend_action=False, check_resource=False, spend_resource=False, setup=setup,
    )
    assert event.save_succeeded is False
    poison = next(item for item in target.state.timed_effects if item.effect_id == "poisoned")
    assert poison.expiry_timing is None and poison.start_of_turn_dice_count == 1

    hp_before = target.state.current_hp
    events, sequence = resolve_start_of_turn_save_condition_damage_events(
        2, 2, target, setup, FixedDiceProvider([4]),
    )
    assert sequence == 3 and events[0].hp_after == hp_before - 4
    recovered, _ = resolve_target_condition_timing(
        3, 2, target, "target_turn_end", FixedDiceProvider([20]), setup,
    )
    assert recovered[0].save_succeeded is True
    assert "poisoned" not in target.state.active_effect_ids


def test_recharge_timed_control_source_proof_fails_closed_but_not_on_card_name() -> None:
    source = _source("dust-mephit")
    renamed = source.model_copy(update={"id": "renamed-source", "name": "Renamed Source"})
    assert _binding("dust-mephit").id == source_proven_recharge_timed_controls_2014(renamed)[0].id
    edited = source.model_copy(update={
        "source_actions": source.source_actions.replace("blinding dust", "glittering dust"),
    })
    assert source_proven_recharge_timed_controls_2014(edited) == []
    assert not supports_recharge_rules_2014(edited)
