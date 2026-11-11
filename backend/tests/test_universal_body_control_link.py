"""Generic body-control ownership is fight-local and reversible."""
from __future__ import annotations

import logging

import pytest

from app.combat.body_control import start_body_control_link, end_body_control_link
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter

logger = logging.getLogger(__name__)


def test_link_lifecycle_validates_save_and_preserves_templates():
    try:
        template = build_demo_fighter()
        owner = build_combatant_state(template)
        host = build_combatant_state(template)
        original = template.model_dump_json()
        kwargs = dict(
            source_action_id="source-control", source_name="Printed Possession",
            round_number=2,
        )
        assert not start_body_control_link(
            "source", owner, "host", host, failed_save=False, **kwargs
        )
        assert host.controlled_by is None
        assert start_body_control_link(
            "source", owner, "host", host, failed_save=True, **kwargs
        )
        assert host.controlled_by.source_id == "source"
        assert host.controlled_by.host_id == "host"
        assert host.controlled_by.started_round == 2
        assert owner.controlling_target_ids == ["host"]
        assert not start_body_control_link(
            "source", owner, "host2", build_combatant_state(template),
            failed_save=True, **kwargs
        )
        assert not end_body_control_link("intruder", owner, "host", host)
        assert end_body_control_link("source", owner, "host", host)
        assert host.controlled_by is None
        assert owner.controlling_target_ids == []
        assert template.model_dump_json() == original
    except Exception:
        logger.exception("Body-control ownership lifecycle test failed")
        raise


def test_invalid_control_links_fail_closed_without_losing_owner():
    try:
        template = build_demo_fighter()
        owner = build_combatant_state(template)
        host = build_combatant_state(template)
        assert not start_body_control_link(
            "same", owner, "same", host,
            source_action_id="control", source_name="Control",
            round_number=1, failed_save=True,
        )
        with pytest.raises(Exception):
            start_body_control_link(
                "owner", owner, "host", host,
                source_action_id="", source_name="Control",
                round_number=1, failed_save=True,
            )
        assert host.controlled_by is None
        assert owner.controlling_target_ids == []
    except Exception:
        logger.exception("Body-control validation test failed")
        raise
