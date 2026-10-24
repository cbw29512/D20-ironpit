"""2014 Shrieker: preserve alarm reaction while using the non-offensive Dodge lane."""
from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_nonactionable_reaction_proofs_2014 import (
    verified_nonactionable_reaction_names_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from scripts.browser_template_serializer import template_row


def _source():
    try:
        return next(
            monster for monster in load_monster_source_2014()
            if monster.id == "shrieker"
        )
    except Exception as exc:
        raise AssertionError("Missing pinned 2014 Shrieker") from exc


def _setup():
    try:
        source = _source()
        template = compile_combatant(adapt_basic_monster_2014(source))
        shrieker = EncounterCombatant(
            combatant_id="shrieker", side="monsters", position_ft=10,
            state=build_combatant_state(template),
        )
        hero = EncounterCombatant(
            combatant_id="hero", side="heroes", position_ft=5,
            state=build_combatant_state(build_demo_fighter()),
        )
        setup = EncounterSetup(
            heroes=[hero], monsters=[shrieker], hero_total_levels=1,
            monster_total_cr="0", ruleset="2014",
        )
        return source, shrieker, hero, setup
    except Exception:
        raise


def test_complete_alarm_clause_is_preserved_but_nonactionable():
    try:
        source = _source()
        snapshot = source.model_dump_json()
        assert verified_nonactionable_reaction_names_2014(source) == frozenset({"Shriek"})
        assert basic_blockers_2014(source) == ()

        template = compile_combatant(adapt_basic_monster_2014(source))
        assert template.weapon_attack is None
        assert template.alternate_weapon_attacks == []
        assert template.source_reaction_names == ["Shriek"]
        assert "False Appearance" in template.source_trait_names

        browser = template_row(template)
        assert browser["attacks"] == []
        assert browser["primary_attack_id"] is None
        assert browser["source_reaction_names"] == ["Shriek"]
        assert source.model_dump_json() == snapshot
    except Exception:
        raise


def test_alarm_reaction_display_name_is_not_dispatch_identity():
    try:
        source = _source()
        renamed = source.model_copy(update={
            "id": "renamed-alarm-plant",
            "name": "Renamed Alarm Plant",
            "reaction_names": ["Alarm Cry"],
            "source_reactions": source.source_reactions.replace(
                "<strong>Shriek.</strong>", "<strong>Alarm Cry.</strong>"
            ),
        })
        assert verified_nonactionable_reaction_names_2014(renamed) == frozenset(
            {"Alarm Cry"}
        )
        assert basic_blockers_2014(renamed) == ()
    except Exception:
        raise


def test_changed_reaction_semantics_fail_closed():
    try:
        source = _source()
        changed = source.model_copy(update={
            "source_reactions": source.source_reactions.replace(
                "audible within 300 feet of it",
                "audible within 300 feet of it and deals 1 fire damage to each listener",
            ),
        })
        assert verified_nonactionable_reaction_names_2014(changed) == frozenset()
        blockers = basic_blockers_2014(changed)
        assert "source:reaction" in blockers
        assert "attack:none" in blockers
    except Exception:
        raise


def test_shrieker_turn_uses_existing_dodge_without_fabricated_attack():
    try:
        source, shrieker, hero, setup = _setup()
        snapshot = source.model_dump_json()
        events, _ = resolve_combat_turn(
            1, 1, shrieker, hero, setup, FixedDiceProvider([10]),
        )
        assert any(event.feature_id == "dodge" for event in events)
        assert not any(event.event_type == "attack" for event in events)
        assert source.model_dump_json() == snapshot
    except Exception:
        raise
