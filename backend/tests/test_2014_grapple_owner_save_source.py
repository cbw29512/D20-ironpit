"""Source-proof held-creature save action against the immutable 327-card corpus."""
from __future__ import annotations

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_save_capabilities_2014 import save_capabilities_2014
from app.content.monster_save_source_audit_2014 import unsupported_source_actions_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.capability_compiler import compile_combatant
from app.content.capability_from_template import definition_from_template
from scripts.browser_template_serializer import _save
from app.content.monster_source_grapple_owner_save_2014 import (
    source_proven_grapple_owner_saves_2014,
)


def test_327_source_scan_proves_only_the_supported_held_creature_save() -> None:
    cards = load_monster_source_2014()
    assert len(cards) == 327
    matched = [
        (monster.id, action)
        for monster in cards
        for action in source_proven_grapple_owner_saves_2014(monster)
    ]
    assert len(matched) == 1
    source_id, action = matched[0]
    assert source_id == "otyugh"
    assert action.name == "Tentacle Slam"
    assert (action.dc, action.range_ft, action.max_targets) == (14, 10, 2)
    assert (action.damage.count, action.damage.size, action.damage.bonus) == (2, 6, 3)
    assert action.success_damage == "half"
    assert action.target_scope == "all-other-creatures"
    assert action.requires_target_grappled_by_source
    assert action.failed_save_timed_effect.effect_id == "stunned"
    assert action.failed_save_timed_effect.expiry_timing == "source_turn_end"
    card = next(card for card in cards if card.id == "otyugh")
    assert len([a for a in save_capabilities_2014(card) if a.name == "Tentacle Slam"]) == 1
    assert "Tentacle Slam" not in unsupported_source_actions_2014(card)
    template = compile_combatant(adapt_monster_mechanics_2014(card))
    runtime = next(a for a in template.saving_throw_actions if a.name == "Tentacle Slam")
    assert runtime.requires_target_grappled_by_source
    assert (runtime.dc, runtime.range_ft, runtime.max_targets) == (14, 10, 2)
    assert runtime.failed_save_timed_effect.effect_id == "stunned"
    assert _save(runtime)["requiresTargetGrappledBySource"] is True
    reconstructed = definition_from_template(template)
    rebuilt = next(a for a in reconstructed.save_actions if a.name == "Tentacle Slam")
    assert rebuilt.requires_target_grappled_by_source


def test_unexpected_rider_and_grapple_capacity_edits_fail_closed() -> None:
    card = next(m for m in load_monster_source_2014() if m.id == "otyugh")
    original = card.model_dump_json()
    altered = card.model_copy(update={
        "source_actions": card.source_actions.replace(
            "isn't stunned", "isn't stunned and can't move",
        ),
    })
    assert source_proven_grapple_owner_saves_2014(altered) == []
    altered = card.model_copy(update={
        "source_actions": card.source_actions.replace("two tentacles", "three tentacles"),
    })
    assert source_proven_grapple_owner_saves_2014(altered) == []
    # Source-specific labels never select runtime mechanics.
    renamed = card.model_copy(update={
        "name": "Renamed Creature",
        "source_actions": card.source_actions.replace("Tentacle Slam", "Crushing Hold")
        .replace("otyugh", "creature"),
    })
    actions = source_proven_grapple_owner_saves_2014(renamed)
    assert len(actions) == 1 and actions[0].name == "Crushing Hold"
    assert actions[0].requires_target_grappled_by_source
    assert card.model_dump_json() == original
