"""2014 Druid prepared spell reuse: verify source identity and existing mechanics."""
from __future__ import annotations

import logging

import pytest

from app.content.capability_compiler import compile_combatant
from app.content.druid_2014_level1_spells import longstrider_2014, produce_flame_2014
from app.content.druid_2014_level2_spells import barkskin_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_prepared_nature_spells_2014 import prepared_nature_spells_2014
from app.content.monster_prepared_spells_2014 import supports_prepared_spellcasting_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_innate_spells_2014 import innate_spell_save_actions_2014
from app.content.shared_nature_spells_2014 import entangle_2014, thunderwave_2014
from app.content.monster_source_shillelagh_2014 import source_shillelagh_buff_2014

logger = logging.getLogger(__name__)
_BOUND = {"druidcraft", "produce-flame", "entangle", "longstrider",
          "speak-with-animals", "thunderwave", "animal-messenger", "barkskin", "shillelagh"}


def test_druid_pinned_source_reuses_all_nine_spells_with_active_shillelagh() -> None:
    try:
        records = {item.id: item for item in load_monster_source_2014()}
        druid = records["druid"]
        before = druid.model_dump_json()
        package = prepared_nature_spells_2014(druid)
        assert package.implemented_ids() == _BOUND
        assert package.saves == (entangle_2014(12), thunderwave_2014(12))
        assert package.attacks == (produce_flame_2014(4, 4),)
        assert package.defenses == (longstrider_2014(), barkskin_2014())
        assert package.buffs == (source_shillelagh_buff_2014(druid),)
        assert supports_prepared_spellcasting_2014(druid)
        assert basic_blockers_2014(druid) == ()

        template = compile_combatant(adapt_monster_mechanics_2014(druid))
        assert {item.id for item in template.spell_save_actions} >= {"entangle", "thunderwave"}
        assert {item.id for item in template.spell_attack_actions} >= {"produce-flame"}
        assert {item.id for item in template.defensive_spell_actions} >= {"barkskin", "longstrider"}
        assert any(action.id == "shillelagh" for action in template.timed_self_buff_actions)
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        assert all("shillelagh" not in attack.id for attack in attacks)
        assert any(attack.conditional_damage for attack in attacks if attack is not None)
        assert {(resource.id, resource.max_uses) for resource in template.resources
                if resource.id.startswith("spell-slot-")} == {
            ("spell-slot-1", 4), ("spell-slot-2", 3),
        }
        assert druid.model_dump_json() == before
        renamed = druid.model_copy(update={"id": "another-caster", "name": "Another Caster"})
        # Source identity can change; weapon IDs are generated from the new
        # source ID but effect semantics are identical.
        renamed_package = prepared_nature_spells_2014(renamed)
        assert renamed_package.implemented_ids() == package.implemented_ids()
        assert renamed_package.buffs[0].modifier_effects[0].weapon_id == "2014-another-caster-quarterstaff"
    except Exception:
        logger.exception("Printed 2014 Druid reuse and fail-closed blocker regressed.")
        raise


@pytest.mark.parametrize("bad", [
    {"id": "entangle", "name": "changed", "level": 1},
    {"id": "thunderwave", "name": "thunderwave", "level": 2},
])
def test_prepared_druid_changed_source_spells_fail_closed(bad) -> None:
    try:
        druid = next(item for item in load_monster_source_2014() if item.id == "druid")
        changed = druid.model_copy(deep=True)
        changed.spellcasting["spells"] = [
            bad if spell["id"] == bad["id"] else spell
            for spell in changed.spellcasting["spells"]
        ]
        with pytest.raises(ValueError, match="Source prepared nature spell"):
            prepared_nature_spells_2014(changed)
        assert prepared_nature_spells_2014(druid).implemented_ids() == _BOUND
    except Exception:
        logger.exception("Prepared 2014 nature source mutation was accepted.")
        raise


def test_2014_entangle_is_the_exact_existing_innate_spell() -> None:
    try:
        dryad = next(item for item in load_monster_source_2014() if item.id == "dryad")
        entangle = next(item for item in innate_spell_save_actions_2014(dryad)
                        if item.id == "entangle")
        assert entangle == entangle_2014(14)
        assert entangle.area.shape == "cube" and entangle.area.length_ft == 20
        assert entangle.failed_save_timed_effect.effect_id == "restrained"
        assert entangle.failed_save_timed_effect.escape_check_dc == 14
        assert entangle.concentration and entangle.creates_difficult_terrain
    except Exception:
        logger.exception("Innate Entangle no longer matches shared 2014 spell.")
        raise


def test_2014_thunderwave_uses_existing_self_cube_and_save_scaling() -> None:
    try:
        wave = thunderwave_2014(12)
        assert (wave.level, wave.save_ability, wave.dc) == (1, "constitution", 12)
        assert (wave.area.shape, wave.area.origin, wave.area.length_ft) == ("cube", "self", 15)
        assert (wave.damage_dice_count, wave.damage_dice_size, wave.damage_type) == (2, 8, "thunder")
        assert wave.success_damage == "half" and wave.failed_save_push_ft == 10
        assert wave.upcast_dice_per_level == 1
    except Exception:
        logger.exception("Shared Thunderwave source or generic area semantics regressed.")
        raise
