from __future__ import annotations

import pytest

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.weapon_catalog import build_weapon
from app.domain.size import CreatureSize


def _attacker(*, mastered: bool = True, level: int = 1, modifier: int | None = 3):
    template = build_karnok_stoneward().model_copy(
        update={"level": level, "weapon_masteries": ["battleaxe"] if mastered else [], "combat_traits": []},
        deep=True,
    )
    state = build_combatant_state(template)
    attack = state.template.weapon_attack.model_copy(
        update={"id": "topple-battleaxe", "weapon": build_weapon("battleaxe"), "attack_ability_modifier": modifier},
        deep=True,
    )
    return state, attack


def _target(*, immune: bool = False, size: CreatureSize = CreatureSize.MEDIUM):
    source = build_goblin_warrior()
    bonuses = dict(source.saving_throw_bonuses)
    bonuses["constitution"] = 0
    template = source.model_copy(
        update={"armor_class": 10, "max_hp": 40, "saving_throw_bonuses": bonuses,
                "condition_immunities": ["prone"] if immune else [], "size": size},
        deep=True,
    )
    return build_combatant_state(template)


def _hit(attacker, defender, attack, values):
    return resolve_attack(1, 1, attacker, defender, attack, 5, FixedDiceProvider(values), spend_action=False)


def test_topple_failed_constitution_save_applies_prone_and_records_save() -> None:
    attacker, attack = _attacker()
    target = _target()

    event = _hit(attacker, target, attack, [15, 4, 5])

    assert event.hit is True
    assert event.save_ability == "constitution"
    assert event.save_dc == 13
    assert event.save_succeeded is False
    assert event.saving_throw_roll is not None and event.saving_throw_roll.total == 5
    assert "prone" in event.applied_condition_ids
    assert "prone" in target.active_effect_ids
    assert "Topple save DC 13" in event.description


def test_topple_success_records_save_without_prone() -> None:
    attacker, attack = _attacker()
    target = _target()

    event = _hit(attacker, target, attack, [15, 4, 18])

    assert event.save_dc == 13
    assert event.save_succeeded is True
    assert "prone" not in event.applied_condition_ids
    assert "prone" not in target.active_effect_ids


def test_topple_has_no_size_restriction() -> None:
    attacker, attack = _attacker()
    target = _target(size=CreatureSize.GARGANTUAN)

    event = _hit(attacker, target, attack, [15, 4, 5])

    assert event.save_succeeded is False
    assert "prone" in target.active_effect_ids


def test_unmastered_topple_weapon_does_not_force_save() -> None:
    attacker, attack = _attacker(mastered=False)
    target = _target()

    event = _hit(attacker, target, attack, [15, 4])

    assert event.save_dc is None
    assert event.saving_throw_roll is None
    assert "prone" not in target.active_effect_ids


def test_topple_skips_save_for_prone_or_immune_target() -> None:
    attacker, attack = _attacker()
    prone = _target(); prone.active_effect_ids.append("prone")
    immune = _target(immune=True)

    prone_event = _hit(attacker, prone, attack, [15, 14, 4])
    immune_event = _hit(attacker, immune, attack, [15, 4])

    assert prone_event.save_dc is None
    assert immune_event.save_dc is None
    assert immune.active_effect_ids == []


def test_topple_dc_scales_with_proficiency_bonus() -> None:
    attacker, attack = _attacker(level=5)
    target = _target()

    event = _hit(attacker, target, attack, [15, 4, 13])

    assert event.save_dc == 14
    assert event.save_succeeded is False


def test_topple_fails_closed_without_explicit_attack_ability_modifier() -> None:
    attacker, attack = _attacker(modifier=None)
    target = _target()

    with pytest.raises(RuntimeError, match="Attack resolution failed"):
        _hit(attacker, target, attack, [15, 4])
