import logging

import pytest
from pydantic import ValidationError

from app.combat.conditions import attack_roll_condition_sources
from app.combat.saving_throw_rolls import saving_throw_mode
from app.content.capability_registry import build_combatant_from_capabilities, get_capability_definition
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.capabilities import CombatantDefinition
from app.domain.models import CombatantState, RollMode

logger = logging.getLogger(__name__)


def _berserker():
    try:
        return build_combatant_from_capabilities("srd-berserker")
    except Exception:
        logger.exception("Failed to compile Berserker capability profile.")
        raise


def _source_row() -> dict[str, object]:
    try:
        rows = [row for row in load_monster_rows() if row["name"] == "Berserker"]
        if len(rows) != 1:
            raise ValueError(f"Expected one Berserker source row; found {len(rows)}.")
        return rows[0]
    except Exception:
        logger.exception("Failed to load Berserker SRD source row.")
        raise


def _state() -> CombatantState:
    template = _berserker()
    return CombatantState(template=template, current_hp=template.max_hp)


def test_berserker_profile_matches_srd() -> None:
    template = _berserker()
    attack = template.weapon_attack
    assert (template.armor_class, template.max_hp, template.speed_ft, template.initiative_bonus) == (13, 67, 30, 1)
    assert (attack.attack_bonus, attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (5, 1, 12, 3)
    assert template.attack_roll_advantage_triggers == ["attacker_bloodied"]
    assert template.saving_throw_advantage_triggers == ["attacker_bloodied"]
    assert template.source_trait_names == ["Bloodied Frenzy"]
    assert template.saving_throw_bonuses == {
        "strength": 3, "dexterity": 1, "constitution": 3,
        "intelligence": -1, "wisdom": 0, "charisma": -1,
    }


def test_berserker_passes_full_srd_source_audit() -> None:
    assert audit_monster_source(_berserker(), _source_row()) == []


def test_bloodied_frenzy_attack_and_save_advantage_use_effective_max_hp() -> None:
    attacker = _state()
    defender = _state()
    assert attack_roll_condition_sources(attacker, defender, 5) == (0, 0)
    assert saving_throw_mode(attacker, "wisdom") is RollMode.NORMAL
    attacker.current_hp = 33
    assert attack_roll_condition_sources(attacker, defender, 5) == (1, 0)
    assert saving_throw_mode(attacker, "wisdom") is RollMode.ADVANTAGE
    attacker.max_hp_bonus = 5
    attacker.current_hp = 35
    assert attack_roll_condition_sources(attacker, defender, 5) == (1, 0)
    assert saving_throw_mode(attacker, "wisdom") is RollMode.ADVANTAGE


def test_bloodied_frenzy_save_advantage_cancels_disadvantage() -> None:
    state = _state()
    state.current_hp = 33
    state.active_effect_ids.append("restrained")
    assert saving_throw_mode(state, "dexterity") is RollMode.NORMAL


def test_bloodied_frenzy_source_audit_requires_both_runtime_halves() -> None:
    source = _source_row()
    template = _berserker()
    no_attack = template.model_copy(update={"attack_roll_advantage_triggers": []})
    no_save = template.model_copy(update={"saving_throw_advantage_triggers": []})
    assert "attack-advantage-runtime-missing:attacker-bloodied" in audit_monster_source(no_attack, source)
    assert "save-advantage-runtime-missing:attacker-bloodied" in audit_monster_source(no_save, source)
    source_without = dict(source)
    source_without["traits"] = ""
    issues = audit_monster_source(template, source_without)
    assert "attack-advantage-source-missing:attacker-bloodied" in issues
    assert "save-advantage-source-missing:attacker-bloodied" in issues


def test_roll_trigger_schema_rejects_unknown_values() -> None:
    definition = get_capability_definition("srd-berserker")
    payload = definition.model_dump(mode="json")
    payload["saving_throw_advantage_triggers"] = ["unknown-trigger"]
    with pytest.raises(ValidationError):
        CombatantDefinition.model_validate(payload)
