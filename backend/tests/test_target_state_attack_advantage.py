from __future__ import annotations

from app.combat.target_state import target_missing_hp_attack_advantage
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_trait_source_audit import trait_issues
from app.domain.models import CombatantState
from app.domain.traits import CombatTrait


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_sahuagin_blood_frenzy_is_source_derived_as_generic_target_state_trait() -> None:
    sahuagin = build_combatant_from_capabilities("srd-sahuagin-warrior")
    assert sahuagin.source_trait_names == ["Blood Frenzy", "Limited Amphibiousness", "Shark Telepathy"]
    assert sahuagin.combat_traits == [CombatTrait.TARGET_MISSING_HP_ATTACK_ADVANTAGE]
    assert trait_issues(sahuagin, _row("Sahuagin Warrior")) == []


def test_target_missing_hp_advantage_uses_effective_max_hp() -> None:
    template = build_combatant_from_capabilities("srd-sahuagin-warrior")
    attacker = CombatantState(template=template, current_hp=template.max_hp)
    target = CombatantState(template=template, current_hp=template.max_hp)

    assert target_missing_hp_attack_advantage(attacker, target) == 0
    target.current_hp -= 1
    assert target_missing_hp_attack_advantage(attacker, target) == 1

    target.max_hp_reduction = 1
    assert target_missing_hp_attack_advantage(attacker, target) == 0


def test_target_missing_hp_advantage_requires_declared_capability() -> None:
    template = build_combatant_from_capabilities("srd-sahuagin-warrior")
    plain = template.model_copy(update={"combat_traits": []})
    attacker = CombatantState(template=plain, current_hp=plain.max_hp)
    target = CombatantState(template=plain, current_hp=plain.max_hp - 1)
    assert target_missing_hp_attack_advantage(attacker, target) == 0
