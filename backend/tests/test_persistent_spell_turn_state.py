from __future__ import annotations

from app.combat.concentration import end_concentration, start_concentration
from app.combat.dice import FixedDiceProvider
from app.combat.persistent_spells import (
    activate_persistent_spell, initial_spell_cast_allowed, persistent_spell_active,
    refresh_spell_turn_state,
)
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.runtime import ResourceState
from app.domain.spells import SpellAttackAction


def _member(combatant_id: str, side: str, position: int) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    template.armor_class = 10
    template.resources = []
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _persistent_attack() -> SpellAttackAction:
    return SpellAttackAction(
        id="persistent-force-weapon",
        name="Persistent Force Weapon",
        level=2,
        action_cost="bonus_action",
        attack_kind="melee",
        range_ft=60,
        attack_bonus=5,
        damage_dice_count=1,
        damage_dice_size=8,
        damage_type="force",
        persistent_duration_rounds=10,
    )


def test_start_turn_snapshot_blocks_new_concentration_until_next_refresh() -> None:
    caster = _member("caster", "heroes", 0)
    start_concentration(caster.state, caster.combatant_id, "fog-cloud", 1)

    refresh_spell_turn_state(caster.state, 2)
    assert caster.state.spell_turn_concentration_locked is True
    assert initial_spell_cast_allowed(caster.state, "insect-plague", concentration=True) is False
    assert initial_spell_cast_allowed(caster.state, "magic-missile", concentration=False) is True

    end_concentration(caster.state)
    assert caster.state.spell_turn_concentration_locked is True
    refresh_spell_turn_state(caster.state, 3)
    assert caster.state.spell_turn_concentration_locked is False
    assert initial_spell_cast_allowed(caster.state, "insect-plague", concentration=True) is True


def test_persistent_spell_expires_only_on_owner_start_turn_refresh() -> None:
    caster = _member("caster", "heroes", 0)
    activate_persistent_spell(caster.state, "persistent-force-weapon", 1, 10)

    refresh_spell_turn_state(caster.state, 10)
    assert persistent_spell_active(caster.state, "persistent-force-weapon") is True
    assert initial_spell_cast_allowed(caster.state, "persistent-force-weapon") is False

    refresh_spell_turn_state(caster.state, 11)
    assert persistent_spell_active(caster.state, "persistent-force-weapon") is False
    assert initial_spell_cast_allowed(caster.state, "persistent-force-weapon") is True


def test_active_persistent_spell_attack_reuses_effect_without_second_slot() -> None:
    caster = _member("caster", "heroes", 0)
    target = _member("target", "monsters", 5)
    setup = EncounterSetup(heroes=[caster], monsters=[target], hero_total_levels=1, monster_total_cr="1")
    caster.state.resources.append(ResourceState(id="spell-slot-2", name="2nd-level slot", current_uses=1, max_uses=1))
    spell = _persistent_attack()

    begin_turn(caster.state)
    refresh_spell_turn_state(caster.state, 1)
    first = resolve_spell_attack(
        1, 1, caster, target, spell, setup, "1:caster", FixedDiceProvider([15, 4]),
    )
    assert first.hit is True
    assert caster.state.resources[0].current_uses == 0
    assert persistent_spell_active(caster.state, spell.id) is True

    begin_turn(caster.state)
    refresh_spell_turn_state(caster.state, 2)
    second = resolve_spell_attack(
        2, 2, caster, target, spell, setup, "2:caster", FixedDiceProvider([15, 4]),
    )
    assert second.hit is True
    assert caster.state.resources[0].current_uses == 0
    assert "already-active spell" in second.description
