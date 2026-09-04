import logging

from app.combat.encounter_setup import build_encounter_setup
from app.content.monster_attack_advantage_source_audit import attack_advantage_issues
from app.domain.models import EncounterSelection

logger = logging.getLogger(__name__)

_SOURCE_ROW = {
    "traits": (
        "Blood Frenzy. The creature has Advantage on attack rolls against any creature "
        "that doesn’t have all its Hit Points."
    ),
    "actions": "Claw. Melee Attack Roll: +3, reach 5 ft. Hit: 4 Slashing damage.",
}


def _template():
    try:
        setup = build_encounter_setup(EncounterSelection(
            hero_ids=["karnok-stoneward-l1"],
            monster_ids=["srd-wolf"],
        ))
        return setup.monsters[0].state.template
    except Exception:
        logger.exception("Failed to build source-audit fixture template.")
        raise


def test_source_mechanic_without_runtime_trigger_fails_closed() -> None:
    template = _template()
    assert attack_advantage_issues(template, _SOURCE_ROW) == [
        "attack-advantage-runtime-missing:target-missing-hit-points"
    ]


def test_runtime_trigger_without_source_mechanic_fails_closed() -> None:
    template = _template().model_copy(update={
        "attack_roll_advantage_triggers": ["target_missing_hit_points"],
    })
    assert attack_advantage_issues(template, {"traits": "", "actions": _SOURCE_ROW["actions"]}) == [
        "attack-advantage-source-missing:target-missing-hit-points"
    ]


def test_matching_source_and_runtime_trigger_pass() -> None:
    template = _template().model_copy(update={
        "attack_roll_advantage_triggers": ["target_missing_hit_points"],
    })
    assert attack_advantage_issues(template, _SOURCE_ROW) == []
