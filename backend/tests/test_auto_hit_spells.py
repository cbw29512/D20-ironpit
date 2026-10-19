from __future__ import annotations

from app.combat.auto_hit_spell_policy import choose_auto_hit_spell
from app.combat.auto_hit_spell_resolution import resolve_auto_hit_spell
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.sorcerer_draconic_2014_runtime import build_nyra_emberveil_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DamageType


def _member(template, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def _setup(level: int = 1, *, resistance: bool = False):
    caster = _member(build_nyra_emberveil_2014(level), "nyra", "heroes", 0)
    target_template = build_commoner().model_copy(update={
        "ruleset": "2014",
        "max_hp": 40,
        "damage_resistances": [DamageType.FORCE] if resistance else [],
    })
    target = _member(target_template, "target", "monsters", 30)
    setup = EncounterSetup(
        heroes=[caster],
        monsters=[target],
        hero_total_levels=level,
        monster_total_cr="0",
        ruleset="2014",
    )
    return setup, caster, target


def test_magic_missile_policy_uses_three_projectiles_at_level_one() -> None:
    setup, caster, target = _setup()

    choice = choose_auto_hit_spell(caster, setup, "1:nyra")

    assert choice is not None
    assert choice.action.id == "magic-missile"
    assert choice.target is target
    assert choice.slot_level == 1
    assert choice.projectile_count == 3
    assert choice.expected_damage == 10.5


def test_magic_missile_resolves_without_attack_or_save_and_spends_slot() -> None:
    setup, caster, target = _setup()
    choice = choose_auto_hit_spell(caster, setup, "1:nyra")
    assert choice is not None

    event = resolve_auto_hit_spell(
        1, 1, caster, target, setup, choice.action,
        choice.slot_level, choice.projectile_count, "1:nyra",
        FixedDiceProvider([1, 2, 3]),
    )

    assert event.feature_id == "magic-missile"
    assert event.attack_roll is None
    assert event.saving_throw_roll is None
    assert event.damage_roll is not None
    assert event.damage_roll.total == 9
    assert len(event.damage_components) == 3
    assert target.state.current_hp == 31
    slot = next(item for item in caster.state.resources if item.id == "spell-slot-1")
    assert slot.current_uses == 1
    assert caster.state.action_available is False


def test_magic_missile_upcasts_by_adding_one_projectile_per_slot_level() -> None:
    setup, caster, _ = _setup(3)
    next(item for item in caster.state.resources if item.id == "spell-slot-1").current_uses = 0

    choice = choose_auto_hit_spell(caster, setup, "1:nyra")

    assert choice is not None
    assert choice.slot_level == 2
    assert choice.projectile_count == 4


def test_auto_hit_projectiles_apply_typed_damage_defenses_per_projectile() -> None:
    setup, caster, target = _setup(resistance=True)
    choice = choose_auto_hit_spell(caster, setup, "1:nyra")
    assert choice is not None

    event = resolve_auto_hit_spell(
        1, 1, caster, target, setup, choice.action,
        choice.slot_level, choice.projectile_count, "1:nyra",
        FixedDiceProvider([4, 4, 4]),
    )

    assert [part.total for part in event.damage_components] == [5, 5, 5]
    assert [part.applied_total for part in event.damage_components] == [2, 2, 2]
    assert event.damage_roll is not None
    assert event.damage_roll.total == 6



def test_renamed_auto_hit_spell_respects_2014_bonus_action_cast_history() -> None:
    """The previous bonus-action spell, not the printed name, blocks the cast."""
    import pytest

    from app.combat.spellcasting import record_spell_turn

    setup, caster, target = _setup()
    action = caster.state.template.auto_hit_spell_actions[0].model_copy(
        update={"id": "synthetic-auto-hit", "name": "Renamed Force Projectiles"},
    )
    key = "1:nyra"
    record_spell_turn(caster.state, key, "bonus_action", 1)
    assert choose_auto_hit_spell(caster, setup, key) is None

    slot = next(item for item in caster.state.resources if item.id == "spell-slot-1")
    remaining, hp_before = slot.current_uses, target.state.current_hp
    with pytest.raises(ValueError, match="conflicts with another cast"):
        resolve_auto_hit_spell(
            1, 1, caster, target, setup, action, 1, 3, key, FixedDiceProvider([]),
        )
    assert slot.current_uses == remaining
    assert target.state.current_hp == hp_before
    assert caster.state.action_available is True


def test_2024_auto_hit_spells_share_one_slot_gate() -> None:
    import pytest

    from app.combat.spellcasting import mark_slot_spell_cast

    setup, caster, target = _setup()
    caster.state.template.ruleset = "2024"
    key = "1:nyra"
    mark_slot_spell_cast(caster.state, key)
    assert choose_auto_hit_spell(caster, setup, key) is None
    slot = next(item for item in caster.state.resources if item.id == "spell-slot-1")
    remaining = slot.current_uses
    action = caster.state.template.auto_hit_spell_actions[0]
    with pytest.raises(ValueError, match="already expended"):
        resolve_auto_hit_spell(
            1, 1, caster, target, setup, action, 1, 3, key, FixedDiceProvider([]),
        )
    assert slot.current_uses == remaining
