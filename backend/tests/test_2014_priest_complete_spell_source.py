"""Priest's complete 2014 prepared spell list compiles to shared combat."""
from __future__ import annotations

import logging

from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_prepared_spells_2014 import supports_prepared_spellcasting_2014
from app.content.monster_priest_spells_2014 import (
    priest_proven_spell_ids_2014, priest_spell_actions_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_priest_spellcasting_2014 import (
    source_proves_priest_spellcasting_2014,
)
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)

_EXPECTED = {
    "light", "sacred-flame", "thaumaturgy", "cure-wounds",
    "guiding-bolt", "sanctuary", "lesser-restoration", "spiritual-weapon",
    "dispel-magic", "spirit-guardians",
}


def _source():
    try:
        return next(card for card in load_monster_source_2014()
                    if card.id == "priest")
    except Exception:
        logger.exception("2014 source Priest missing from canonical roster.")
        raise


def test_full_327_card_source_match_and_fail_closed_classification():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        assert [card.id for card in cards
                if source_proves_priest_spellcasting_2014(card)] == ["priest"]
        card = _source()
        before = card.model_dump_json()
        assert priest_proven_spell_ids_2014(card) == _EXPECTED
        assert supports_prepared_spellcasting_2014(card)
        assert basic_blockers_2014(card) == ()
        assert card.model_dump_json() == before
        package = priest_spell_actions_2014(card)
        assert all((
            package.saves, package.attacks, package.healing,
            package.defenses, package.condition_removals,
            package.effect_removals, package.persistent_attacks,
            package.timed_buffs,
        ))
    except Exception:
        logger.exception("Full 2014 Priest spell audit or classification failed.")
        raise


def test_real_priest_runtime_and_browser_have_all_eight_spells_and_slots():
    try:
        card = _source()
        before = card.model_dump_json()
        # Source projection must preserve the persistent action before the
        # shared schema/compiler boundary, not just in the spell package.
        definition = adapt_basic_monster_2014(card)
        assert [a.id for a in definition.persistent_spell_attack_actions] == [
            "spiritual-weapon",
        ]
        template = compile_combatant(definition)
        row = template_row(template)
        assert [a.id for a in template.spell_save_actions] == ["sacred-flame"]
        assert [a.id for a in template.spell_attack_actions] == ["guiding-bolt"]
        assert [a.id for a in template.healing_actions] == ["cure-wounds"]
        assert [a.id for a in template.defensive_spell_actions] == ["sanctuary"]
        assert [a.id for a in template.condition_removal_actions] == ["lesser-restoration"]
        assert [a.id for a in template.effect_removal_actions] == ["dispel-magic"]
        assert [a.id for a in template.persistent_spell_attack_actions] == ["spiritual-weapon"]
        assert "spirit-guardians" in [a.id for a in template.timed_self_buff_actions]
        assert "Divine Eminence" in template.source_trait_names
        assert "Spellcasting" in template.source_trait_names

        slots = {a.id: a.max_uses for a in template.resources}
        assert slots == {"spell-slot-1": 4, "spell-slot-2": 3, "spell-slot-3": 2}
        assert {a.id: a.current_uses for a in build_combatant_state(template).resources} == slots
        assert row["resources"] == slots
        assert row["ruleset"] == "2014"
        assert row["id"] == "2014-priest"
        assert [a["id"] for a in row["persistent_spell_attack_actions"]] == [
            "spiritual-weapon",
        ]
        assert [a["id"] for a in row["effect_removal_actions"]] == ["dispel-magic"]

        sacred, = template.spell_save_actions
        assert (sacred.dc, sacred.damage_dice_count, sacred.damage_dice_size) == (
            13, 2, 8,
        )
        guiding, = template.spell_attack_actions
        assert (guiding.attack_bonus, guiding.damage_dice_count,
                guiding.damage_dice_size) == (5, 4, 6)
        healing, = template.healing_actions
        assert healing.healing_bonus == (card.abilities["wis"] - 10) // 2
        spiritual, = template.persistent_spell_attack_actions
        assert spiritual.attack.attack_bonus == 5
        assert spiritual.attack.damage_bonus == healing.healing_bonus
        guardians, = [a for a in template.timed_self_buff_actions
                      if a.id == "spirit-guardians"]
        zone = guardians.start_turn_emanation_damage
        assert guardians.concentration and zone is not None
        assert (zone.radius_ft, zone.dice_count, zone.dice_size, zone.save_dc) == (
            15, 3, 8, 13,
        )
        assert card.model_dump_json() == before
    except Exception:
        logger.exception("2014 Priest source-to-Python/browser spell fidelity failed.")
        raise
