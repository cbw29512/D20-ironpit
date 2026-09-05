from app.combat.encounter_setup import build_encounter_setup
from app.combat.saving_throw_rolls import saving_throw_mode
from app.content.monster_attack_advantage_source_audit import attack_advantage_issues, source_advantage_triggers
from app.domain.models import EncounterSelection, RollMode

_MAGIC_RESISTANCE_ROW = {
    "traits": "Magic Resistance. The creature has Advantage on saving throws against spells and other magical effects.",
    "actions": "Claw. Melee Attack Roll: +3, reach 5 ft. Hit: 4 Slashing damage.",
}


def _state():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-wolf"],
    ))
    base = setup.monsters[0].state
    template = base.template.model_copy(update={"saving_throw_advantage_triggers": ["magical_effect"]})
    return base.model_copy(update={"template": template})


def test_magic_resistance_only_applies_to_magical_saves() -> None:
    state = _state()
    assert saving_throw_mode(state, "wisdom") is RollMode.NORMAL
    assert saving_throw_mode(state, "wisdom", magical=True) is RollMode.ADVANTAGE


def test_magic_resistance_source_compiles_to_generic_save_trigger() -> None:
    attack, saves = source_advantage_triggers(_MAGIC_RESISTANCE_ROW)
    assert attack == []
    assert saves == ["magical_effect"]


def test_magic_resistance_source_audit_fails_closed_both_directions() -> None:
    base = _state().template.model_copy(update={"saving_throw_advantage_triggers": []})
    assert attack_advantage_issues(base, _MAGIC_RESISTANCE_ROW) == [
        "save-advantage-runtime-missing:magical-effect"
    ]
    runtime = base.model_copy(update={"saving_throw_advantage_triggers": ["magical_effect"]})
    assert attack_advantage_issues(runtime, {"traits": "", "actions": _MAGIC_RESISTANCE_ROW["actions"]}) == [
        "save-advantage-source-missing:magical-effect"
    ]
    assert attack_advantage_issues(runtime, _MAGIC_RESISTANCE_ROW) == []
