from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellAttackAction


def _member(combatant_id: str, side: str, position: int, armor_class: int = 20) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    template.armor_class = armor_class
    template.resources = []
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_miss_half_applies_half_cantrip_damage_without_riders() -> None:
    caster = _member("caster", "heroes", 0)
    target = _member("target", "monsters", 30, armor_class=20)
    setup = EncounterSetup(heroes=[caster], monsters=[target], hero_total_levels=1, monster_total_cr="1")
    hp_before = target.state.current_hp
    spell = SpellAttackAction(
        id="fire-bolt",
        name="Fire Bolt",
        level=0,
        attack_kind="ranged",
        range_ft=120,
        attack_bonus=0,
        damage_dice_count=1,
        damage_dice_size=10,
        damage_type="fire",
        miss_damage="half",
    )

    event = resolve_spell_attack(
        1, 1, caster, target, spell, setup, "1:caster",
        FixedDiceProvider([2, 8]),
    )

    assert event.hit is False
    assert event.critical is False
    assert event.applied_condition_ids == []
    assert event.hp_after == hp_before - 4
    assert event.damage_roll is not None
    assert event.damage_roll.total == 4
