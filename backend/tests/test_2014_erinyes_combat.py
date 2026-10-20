"""Actual source card through the universal Python attack pipeline."""
import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_magic_cured_condition_2014 import source_completed_magic_cured_condition_2014
from app.domain.models import DamageType

logger = logging.getLogger(__name__)


def _fight(rolls, *, renamed=False, defended=False):
    try:
        source = next(row for row in load_monster_source_2014() if row.id == "erinyes")
        original = source.model_dump_json()
        template = compile_combatant(adapt_basic_monster_2014(source))
        bow = next(attack for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
                   if attack.weapon.name == "Longbow").model_copy(deep=True)
        if renamed:
            # Source identity and display labels are not combat dispatch keys.
            template = template.model_copy(update={"id": "other-archer", "name": "Other Archer", "kind": "character"})
            bow.id = "other-arrow"
            bow.weapon.id = "other-weapon"
            bow.weapon.name = "Venom Arrow"
        target_template = build_demo_fighter().model_copy(deep=True)
        target_template.max_hp = 200
        target_template.armor_class = 10
        target_template.saving_throw_bonuses["constitution"] = 0
        if defended:
            target_template.damage_resistances = [DamageType.PIERCING]
            target_template.damage_immunities = [DamageType.POISON]
            target_template.condition_immunities = ["poisoned"]
        attacker = build_combatant_state(template)
        target = build_combatant_state(target_template)
        event = resolve_attack(
            1, 1, attacker, target, bow, 60, FixedDiceProvider(rolls),
            actor_event_id="archer", target_event_id="target", close_enemy_active=False,
        )
        assert source.model_dump_json() == original
        return event, target
    except Exception:
        logger.exception("Source-bound Erinyes attack regression failed (renamed=%s, defended=%s).", renamed, defended)
        raise


def test_real_card_hit_has_two_damage_types_and_one_failed_condition_save():
    try:
        event, target = _fight([15, 2, 2, 2, 2, 1])
        assert event.hit and not event.critical
        assert event.damage_roll.total == 11
        assert [part.damage_type for part in event.damage_components] == [DamageType.PIERCING, DamageType.POISON]
        assert event.save_dc == 14 and event.save_succeeded is False
        assert target.current_hp == 189 and "poisoned" in target.active_effect_ids
        assert not target.timed_effects
        assert "poisoned" not in build_combatant_state(target.template).active_effect_ids
    except Exception:
        logger.exception("Erinyes full-hit/save/reset assertions failed.")
        raise


def test_condition_save_success_does_not_prevent_printed_poison_damage():
    try:
        event, target = _fight([15, 2, 2, 2, 2, 20])
        assert event.save_succeeded is True
        assert event.damage_roll.total == 11 and target.current_hp == 189
        assert "poisoned" not in target.active_effect_ids
    except Exception:
        logger.exception("Erinyes successful condition save changed independent damage.")
        raise


def test_miss_and_typed_defenses_use_existing_universal_resolution():
    try:
        missed, untouched = _fight([2])
        assert missed.hit is False and untouched.current_hp == 200
        assert "poisoned" not in untouched.active_effect_ids
        defended, immune = _fight([15, 2, 2, 2, 2], defended=True)
        assert defended.damage_roll.total == 2 and immune.current_hp == 198
        assert "poisoned" not in immune.active_effect_ids
    except Exception:
        logger.exception("Erinyes miss/typed-defense assertions failed.")
        raise


def test_renamed_character_card_reuses_identical_attack_damage_and_save():
    try:
        event, target = _fight([15, 2, 2, 2, 2, 1], renamed=True)
        assert event.hit and event.damage_roll.total == 11
        assert event.save_succeeded is False and "poisoned" in target.active_effect_ids
        assert "Venom Arrow" in event.description
    except Exception:
        logger.exception("Renamed character failed to reuse the source-bound attack.")
        raise


def test_unprinted_effect_cannot_complete_an_attack():
    try:
        source = next(row for row in load_monster_source_2014() if row.id == "erinyes")
        bow = next(attack for attack in source.attacks if attack.id == "longbow")
        for field, value in (
            ("conditional_attack_advantage", [{"unknown": True}]),
            ("control_effect", {}), ("ongoing_damage_effect", {}),
            ("on_hit_ability_score_reduction", {"ability": "strength"}),
            ("on_hit_contested_movement", {}), ("resource_id", "unknown"),
            ("breakable_restraint", {}), ("charge_profile", {}),
            ("forbid_target_grappled_by_self", True), ("grapple_target_policy", "unknown"),
        ):
            changed = bow.model_copy(update={field: value})
            assert not source_completed_magic_cured_condition_2014(source, changed).source_complete
    except Exception:
        logger.exception("Unsupported source metadata was admitted by the condition binder.")
        raise
