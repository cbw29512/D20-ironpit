"""2014 Storm Giant source audit: utility spells cannot sideline its combat Actions."""
from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.capability_compiler import compile_combatant
from app.content.monster_environmental_spell_proofs_2014 import (
    source_proven_arena_inert_innate_spells_2014,
)
from app.content.monster_innate_support_2014 import (
    supports_innate_spellcasting_2014,
    innate_spell_resources_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def _source():
    try:
        rows = load_monster_source_2014()
        assert len(rows) == 327
        return next(monster for monster in rows if monster.id == "storm-giant")
    except Exception:
        logger.exception("2014 Storm Giant source record missing.")
        raise


def test_storm_giant_fights_with_existing_melee_ranged_and_lightning_actions():
    try:
        source = _source()
        snapshot = source.model_dump_json()
        neutral = source_proven_arena_inert_innate_spells_2014(source)
        assert neutral == {
            "feather-fall", "levitate", "light",
            "control-weather", "water-breathing",
        }
        assert supports_innate_spellcasting_2014(source)
        assert basic_blockers_2014(source) == ()
        assert innate_spell_resources_2014(source) == []

        template = compile_combatant(adapt_basic_monster_2014(source))
        assert template.name == "Storm Giant"
        assert template.weapon_attack is not None
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        assert {(attack.weapon.name, attack.attack_bonus) for attack in attacks} == {
            ("Greatsword", 14), ("Rock", 14),
        }
        assert all(attack.id in {"greatsword", "rock"} for attack in attacks)
        assert template.attack_action is not None
        assert len(template.attack_action.slots) == 2
        assert all(slot.attack_ids == ["greatsword"] for slot in template.attack_action.slots)
        lightning = next(
            action for action in template.saving_throw_actions
            if action.id == "lightning-strike"
        )
        assert lightning.dc == 17
        assert lightning.save_ability == "dexterity"
        assert lightning.damage_dice_count == 12
        assert lightning.damage_dice_size == 8
        assert lightning.damage_type == "lightning"
        assert lightning.success_damage == "half"
        assert lightning.resource_id == "lightning-strike"
        assert not template.spell_save_actions
        assert not template.timed_self_buff_actions
        assert source.model_dump_json() == snapshot
    except Exception:
        logger.exception("Storm Giant standard melee/ranged/lightning proof failed.")
        raise


def test_environment_spell_proof_is_name_independent_but_fails_on_source_drift():
    try:
        original = _source()
        renamed = original.model_copy(update={
            "id": "renamed-utility-caster", "name": "Source Caster",
        })
        assert source_proven_arena_inert_innate_spells_2014(renamed)
        # This proof is source/metadata driven, not keyed to a monster ID.
        for before, after in (
            ("feather fall", "feather fall, fireball"),
            ("levitate", "lightning bolt"),
            ("control weather", "control thunderstorms"),
            ("water breathing", "water walk"),
            ("spell save DC 17", "spell save DC 18"),
        ):
            assert before in original.source_traits
            changed = original.model_copy(update={
                "source_traits": original.source_traits.replace(before, after),
            })
            assert not source_proven_arena_inert_innate_spells_2014(changed)
            assert not supports_innate_spellcasting_2014(changed)
            assert "mechanic:spellcasting" in basic_blockers_2014(changed)
        # Never silently turn newly declared combat spells into environmental utility.
        innate = dict(original.innate_spellcasting)
        innate["spells"] = [*innate["spells"], {
            "id": "fireball", "name": "fireball",
            "usage": "per_day", "uses_per_day": 1,
            "shared_pool": False, "qualifier": None,
        }]
        changed = original.model_copy(update={"innate_spellcasting": innate})
        assert not source_proven_arena_inert_innate_spells_2014(changed)
    except Exception:
        logger.exception("Noncombat environment spell source mutation check failed.")
        raise
