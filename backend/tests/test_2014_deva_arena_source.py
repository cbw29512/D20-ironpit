"""Source-faithful 2014 Deva admission without conjuring noncombat behavior."""
from __future__ import annotations

import logging

from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_change_shape_policy_2014 import (
    approved_inert_change_shape_2014,
    source_proven_inert_voluntary_form_2014,
)
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.capability_compiler import compile_combatant
from app.content.monster_innate_source_2014 import (
    ARENA_NEUTRAL_INNATE_SPELLS_2014, innate_spells_2014,
)
from app.content.monster_innate_support_2014 import (
    supports_innate_spellcasting_2014, innate_spell_names_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def _deva():
    try:
        catalog = load_monster_source_2014()
        assert len(catalog) == 327
        return next(x for x in catalog if x.id == "deva")
    except Exception:
        logger.exception("Could not load source Deva record.")
        raise


def test_deva_keeps_melee_and_healing_without_noncombat_spells():
    try:
        card = _deva()
        source_snapshot = card.model_dump_json()
        assert [x["id"] for x in innate_spells_2014(card)] == [
            "detect-evil-and-good", "commune", "raise-dead",
        ]
        assert {"commune", "raise-dead"} <= ARENA_NEUTRAL_INNATE_SPELLS_2014
        assert supports_innate_spellcasting_2014(card)
        assert innate_spell_names_2014(card) == set()
        assert source_proven_inert_voluntary_form_2014(card)
        assert approved_inert_change_shape_2014(card)
        assert basic_blockers_2014(card) == ()

        template = compile_combatant(adapt_monster_mechanics_2014(card))
        assert template.name == "Deva"
        assert template.max_hp == card.max_hp
        assert template.weapon_attack is not None
        assert template.weapon_attack.name == "Mace"
        assert template.healing_actions
        assert any(item.name == "Healing Touch" for item in template.healing_actions)
        assert not template.persistent_barrier_actions
        assert not template.spell_save_actions
        assert not template.timed_self_buff_actions
        assert card.model_dump_json() == source_snapshot
    except Exception:
        logger.exception("Deva 2014 source-classification or combat schema failed.")
        raise


def test_deva_shape_proof_is_complete_and_source_identity_independent():
    try:
        card = _deva()
        expected = source_sections_2014(
            card.source_actions, include_continuations=True,
        )["Change Shape"]
        assert "AC, movement modes" in expected
        assert "statistics and capabilities" in expected
        renamed = card.model_copy(update={"id": "anonymous-celestial", "name": "Other"})
        assert source_proven_inert_voluntary_form_2014(renamed)

        for old, new in (
            ("challenge rating equal to or less than", "challenge rating above"),
            ("reverts to its true form if it dies", "changes form on death"),
            ("AC, movement modes", "hit points, movement modes"),
            ("except class features", "including class features"),
        ):
            assert old in card.source_actions
            changed = card.model_copy(update={
                "source_actions": card.source_actions.replace(old, new),
            })
            assert not source_proven_inert_voluntary_form_2014(changed)
            assert "source:extra-action" in basic_blockers_2014(changed)
    except Exception:
        logger.exception("Deva full Change Shape mutation policy failed.")
        raise


def test_unknown_innate_spell_restores_real_spellcasting_blocker():
    try:
        card = _deva()
        original = card.innate_spellcasting
        assert isinstance(original, dict)
        altered = dict(original)
        altered["spells"] = [*original["spells"], {
            "id": "unknown-future-spell", "name": "unknown future spell",
            "usage": "per_day", "uses_per_day": 1,
        }]
        changed = card.model_copy(update={"innate_spellcasting": altered})
        assert not supports_innate_spellcasting_2014(changed)
        assert "mechanic:spellcasting" in basic_blockers_2014(changed)
    except Exception:
        logger.exception("Deva unknown future spell safety regression failed.")
        raise
