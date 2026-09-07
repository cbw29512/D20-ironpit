from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_goblin_warrior
from app.content.simple_monster_source_definitions import build_simple_source_definitions


def _ghoul():
    template = compile_combatant(build_simple_source_definitions()["srd-ghoul"])
    state = build_combatant_state(template)
    attack = next(item for item in [state.template.weapon_attack, *state.template.alternate_weapon_attacks] if item.weapon.name == "Claw")
    return state, attack


def _target(*, creature_type: str | None = "Humanoid", species_id: str | None = None):
    source = build_goblin_warrior(); bonuses = dict(source.saving_throw_bonuses); bonuses["constitution"] = 0
    template = source.model_copy(update={
        "armor_class": 10, "max_hp": 40, "saving_throw_bonuses": bonuses,
        "creature_type": creature_type, "species_id": species_id,
    }, deep=True)
    return build_combatant_state(template)


def _dice_for(attack, save_roll: int | None):
    values = [15, *([2] * attack.weapon.dice_count)]
    if save_roll is not None: values.append(save_roll)
    return FixedDiceProvider(values)


def test_failed_hit_save_applies_paralyzed_with_printed_timing() -> None:
    ghoul, claw = _ghoul(); target = _target()
    event = resolve_attack(1, 1, ghoul, target, claw, 5, _dice_for(claw, 5), spend_action=False)
    assert event.hit is True and event.save_ability == "constitution" and event.save_dc == 10
    assert event.save_succeeded is False and "paralyzed" in event.applied_condition_ids
    effect = next(item for item in target.timed_effects if item.effect_id == "paralyzed")
    assert effect.expiry_timing == "target_turn_end" and effect.source_effect_id == claw.id
    assert "Claw" in event.description and "Paralyzed" in event.description


def test_successful_hit_save_does_not_apply_condition() -> None:
    ghoul, claw = _ghoul(); target = _target()
    event = resolve_attack(1, 1, ghoul, target, claw, 5, _dice_for(claw, 20), spend_action=False)
    assert event.save_succeeded is True and "paralyzed" not in target.active_effect_ids


def test_hit_save_rider_respects_creature_type_and_species_exclusions() -> None:
    for target in (_target(creature_type="Undead"), _target(species_id="elf")):
        ghoul, claw = _ghoul()
        event = resolve_attack(1, 1, ghoul, target, claw, 5, _dice_for(claw, None), spend_action=False)
        assert event.save_dc is None and event.saving_throw_roll is None
        assert "paralyzed" not in target.active_effect_ids
