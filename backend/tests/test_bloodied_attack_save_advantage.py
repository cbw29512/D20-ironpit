from __future__ import annotations

from app.combat.bloodied import bloodied_attack_advantage, bloodied_save_advantage, is_bloodied
from app.combat.saving_throw_rolls import saving_throw_mode
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_trait_source_audit import trait_issues
from app.domain.models import CombatantState, RollMode
from app.domain.traits import CombatTrait


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_berserker_bloodied_frenzy_is_source_derived_as_generic_trait() -> None:
    berserker = build_combatant_from_capabilities("srd-berserker")
    assert berserker.source_trait_names == ["Bloodied Frenzy"]
    assert berserker.combat_traits == [CombatTrait.BLOODIED_ATTACK_SAVE_ADVANTAGE]
    assert trait_issues(berserker, _row("Berserker")) == []


def test_bloodied_attack_save_advantage_uses_effective_max_hp() -> None:
    template = build_combatant_from_capabilities("srd-berserker")
    state = CombatantState(template=template, current_hp=template.max_hp)

    state.current_hp = template.max_hp // 2
    assert is_bloodied(state)
    assert bloodied_attack_advantage(state) == 1
    assert bloodied_save_advantage(state) == 1
    assert saving_throw_mode(state, "wisdom") is RollMode.ADVANTAGE

    state.max_hp_reduction = 2
    assert not is_bloodied(state)
    assert bloodied_attack_advantage(state) == 0
    assert bloodied_save_advantage(state) == 0


def test_bloodied_save_advantage_cancels_restrained_dexterity_disadvantage() -> None:
    template = build_combatant_from_capabilities("srd-berserker")
    state = CombatantState(template=template, current_hp=template.max_hp // 2)
    state.active_effect_ids.append("restrained")
    assert saving_throw_mode(state, "dexterity") is RollMode.NORMAL
