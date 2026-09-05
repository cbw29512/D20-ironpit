from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import add_modifier, next_attack_against_advantage_sources, next_attack_disadvantage_sources
from app.combat.spell_attack_resolution import resolve_spell_attack
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.spells import SpellAttackAction


def _member(combatant_id: str, side: str, position: int, armor_class: int = 10) -> EncounterCombatant:
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


def _spell(*, attack_kind: str = "ranged") -> SpellAttackAction:
    return SpellAttackAction(
        id="test-spell-attack",
        name="Test Spell Attack",
        level=0,
        attack_kind=attack_kind,
        range_ft=120 if attack_kind == "ranged" else 5,
        attack_bonus=5,
        damage_dice_count=1,
        damage_dice_size=8,
        damage_type="force",
    )


def _setup(distance: int = 30, target_ac: int = 10):
    caster = _member("caster", "heroes", 0)
    target = _member("target", "monsters", distance, target_ac)
    setup = EncounterSetup(heroes=[caster], monsters=[target], hero_total_levels=1, monster_total_cr="1")
    return caster, target, setup


def _study(caster: EncounterCombatant, target: EncounterCombatant) -> None:
    add_modifier(caster.state, CombatModifier(
        id="study-target",
        source_id=caster.combatant_id,
        source_effect_id="studied-attacks",
        kind=ModifierKind.NEXT_ATTACK_AGAINST_ADVANTAGE,
        target_id=target.combatant_id,
    ))


def _sap(caster: EncounterCombatant) -> None:
    add_modifier(caster.state, CombatModifier(
        id="enemy:weapon-mastery-sap",
        source_id="enemy",
        source_effect_id="weapon-mastery-sap",
        kind=ModifierKind.NEXT_ATTACK_DISADVANTAGE,
        expires_at_start_of_source_turn=True,
    ))


def test_spell_attack_consumes_target_scoped_next_attack_advantage() -> None:
    caster, target, setup = _setup(target_ac=15)
    _study(caster, target)

    event = resolve_spell_attack(
        1, 1, caster, target, _spell(), setup, "1:caster",
        FixedDiceProvider([2, 15, 4]),
    )

    assert event.attack_roll is not None and event.attack_roll.mode.value == "advantage"
    assert event.hit is True
    assert next_attack_against_advantage_sources(caster.state, target.combatant_id) == 0


def test_spell_attack_gets_advantage_against_reckless_target() -> None:
    caster, target, setup = _setup(target_ac=15)
    target.state.active_effect_ids.append("reckless-attack")

    event = resolve_spell_attack(
        1, 1, caster, target, _spell(), setup, "1:caster",
        FixedDiceProvider([2, 15, 4]),
    )

    assert event.attack_roll is not None and event.attack_roll.mode.value == "advantage"
    assert event.hit is True


def test_spell_attack_sap_disadvantage_cancels_advantage_and_is_consumed() -> None:
    caster, target, setup = _setup(target_ac=15)
    _study(caster, target)
    _sap(caster)

    event = resolve_spell_attack(
        1, 1, caster, target, _spell(), setup, "1:caster",
        FixedDiceProvider([15, 4]),
    )

    assert event.attack_roll is not None and event.attack_roll.mode.value == "normal"
    assert event.hit is True
    assert next_attack_against_advantage_sources(caster.state, target.combatant_id) == 0
    assert next_attack_disadvantage_sources(caster.state) == 0


def test_spell_attack_heroic_inspiration_can_recover_a_miss() -> None:
    caster, target, setup = _setup(target_ac=15)
    caster.state.heroic_inspiration = True

    event = resolve_spell_attack(
        1, 1, caster, target, _spell(), setup, "1:caster",
        FixedDiceProvider([2, 15, 4]),
    )

    assert event.hit is True
    assert caster.state.heroic_inspiration is False
    assert "Heroic Inspiration rerolls one d20" in event.description


def test_melee_spell_attack_does_not_take_ranged_close_combat_disadvantage() -> None:
    caster, target, setup = _setup(distance=5, target_ac=15)

    melee = resolve_spell_attack(
        1, 1, caster, target, _spell(attack_kind="melee"), setup, "1:caster",
        FixedDiceProvider([15, 4]),
    )

    assert melee.attack_roll is not None and melee.attack_roll.mode.value == "normal"
    assert melee.hit is True


def test_ranged_spell_attack_still_takes_close_combat_disadvantage() -> None:
    caster, target, setup = _setup(distance=5, target_ac=30)

    ranged = resolve_spell_attack(
        1, 1, caster, target, _spell(), setup, "1:caster",
        FixedDiceProvider([18, 2]),
    )

    assert ranged.attack_roll is not None and ranged.attack_roll.mode.value == "disadvantage"
    assert ranged.attack_roll.selected_roll == 2
