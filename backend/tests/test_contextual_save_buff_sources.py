from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_catalog import load_monster_rows
from app.content.monster_contextual_save_defenses import contextual_save_defenses_2014, contextual_save_defenses_from_source
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.timed_self_buffs import TimedSelfBuffAction


def test_full_source_family_has_two_2014_users_and_no_2024_backport():
    matches = {}
    for source in load_monster_source_2014():
        actions, grants = contextual_save_defenses_2014(source)
        if actions or grants:
            matches[source.name] = actions, grants
    assert set(matches) == {"Ghast", "Lich"}
    aura = matches["Ghast"][0][0]
    assert (aura.name, aura.activation_timing, aura.duration_rounds, aura.resource_id) == ("Turning Defiance", "passive", None, None)
    assert aura.friendly_save_advantage_aura.radius_ft == 30
    assert aura.friendly_save_advantage_aura.target_template_ids == ["2014-ghoul"]
    assert aura.friendly_save_advantage_aura.covers_arena
    assert aura.friendly_save_advantage_aura.recipient_scope == "all"
    assert aura.friendly_save_advantage_aura.includes_source
    assert aura.friendly_save_advantage_aura.required_effect_tags == ["turning"]
    grant, = matches["Lich"][1]
    assert grant.source_name == "Turn Resistance" and grant.source_id == "turn-resistance"
    assert grant.required_effect_tags == ["turning"] and len(grant.abilities) == 6
    assert not grant.requires_magical_effect
    for row in load_monster_rows():
        assert contextual_save_defenses_from_source(row.get("traits"), "2024") == ([], [])


def test_both_names_are_bound_but_lich_unrelated_mechanics_stay_blocked():
    ghast = next(m for m in load_monster_source_2014() if m.name == "Ghast")
    lich = next(m for m in load_monster_source_2014() if m.name == "Lich")
    assert basic_blockers_2014(ghast) == ()
    assert "Turn Resistance" not in unsupported_traits_2014(lich)
    assert basic_blockers_2014(lich)


def test_source_heading_is_metadata_and_unknown_recipients_fail_closed():
    ghast = next(m for m in load_monster_source_2014() if m.name == "Ghast")
    text = ghast.source_traits.replace("Turning Defiance", "Grave Ward")
    actions, _ = contextual_save_defenses_from_source(text, "2014", {"ghouls": "arbitrary-template"})
    assert actions[0].name == "Grave Ward"
    assert actions[0].friendly_save_advantage_aura.target_template_ids == ["arbitrary-template"]
    with pytest.raises(ValueError, match="recipient"):
        contextual_save_defenses_from_source(text, "2014")


def test_passive_save_buff_schema_rejects_activation_and_mixed_aura_payloads():
    ghast = next(m for m in load_monster_source_2014() if m.name == "Ghast")
    action, = contextual_save_defenses_2014(ghast)[0]
    payload = action.model_dump()
    for invalid in [{"resource_id": "charge"}, {"condition_ids": ["invisible"]}, {"duration_rounds": 1}]:
        with pytest.raises(ValueError):
            TimedSelfBuffAction.model_validate({**payload, **invalid})
    payload["friendly_save_advantage_aura"]["target_template_ids"] = [""]
    with pytest.raises(ValueError):
        TimedSelfBuffAction.model_validate(payload)


def test_browser_lich_fixture_matches_actual_source_grant():
    lich = next(m for m in load_monster_source_2014() if m.name == "Lich")
    expected = {"saving_throw_advantage_grants": [g.model_dump(mode="json") for g in contextual_save_defenses_2014(lich)[1]]}
    fixture = Path(__file__).resolve().parents[2] / "frontend/test-fixtures/turn-resistance-2014.json"
    assert json.loads(fixture.read_text()) == expected
