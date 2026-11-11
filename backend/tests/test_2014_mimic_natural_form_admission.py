"""2014 natural-form Mimic uses universal attacks, never object-form Adhesive."""
from __future__ import annotations

import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_natural_form_only_2014 import (
    proven_natural_form_only_traits_2014,
    source_completed_natural_form_attack_2014,
)
from app.content.monster_source_grapple_attack_advantage_2014 import (
    source_grapple_attack_advantage_2014,
)
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _mimic():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        return next(card for card in cards if card.id == "mimic")
    except Exception:
        logger.exception("Could not find pinned 2014 Mimic")
        raise


def test_mimic_natural_form_is_a_complete_basic_candidate():
    try:
        card = _mimic()
        source = card.model_dump_json()
        assert [item.trigger for item in source_grapple_attack_advantage_2014(card)] == [
            "target_grappled_by_self",
        ]
        assert proven_natural_form_only_traits_2014(card) == {
            "Adhesive (Object Form Only)", "False Appearance (Object Form Only)",
        }
        pseudo = next(attack for attack in card.attacks if attack.id == "pseudopod")
        corrected = source_completed_natural_form_attack_2014(card, pseudo)
        assert corrected.source_complete and corrected.damage.average == 7
        assert corrected.control_effect is None
        # The source changes form only through its printed Shapechanger Action;
        # that Action is excluded by the Pit, so object-form riders cannot fire.
        assert "Shapechanger" in card.trait_names
        assert "If the mimic is in object form" in card.source_actions
        assert card.source_actions.count("If the mimic is in object form") == 1
        assert basic_blockers_2014(card) == ()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        row = template_row(template)
        assert len(row["attacks"]) == 2
        attack = next(item for item in row["attacks"] if item["name"] == "Pseudopod")
        assert (attack["bonus"], attack["diceCount"], attack["diceSize"],
                attack["damageBonus"]) == (5, 1, 8, 3)
        assert "controlEffect" not in attack
        assert attack["conditionalAttackAdvantage"] == [
            {"trigger": "target_grappled_by_self"}
        ]
        bite = next(item for item in row["attacks"] if item["name"] == "Bite")
        assert bite["onHitDamage"][0]["damageType"] == "acid"
        assert bite["conditionalAttackAdvantage"] == attack["conditionalAttackAdvantage"]
        assert card.model_dump_json() == source
    except Exception:
        logger.exception("Mimic natural-form compilation/admission failed")
        raise


def test_unknown_object_form_clause_restores_blocker():
    try:
        card = _mimic()
        original = card.model_dump_json()
        changes = [
            ("If the mimic is in object form", "If the mimic is in natural form"),
            ("escape DC 13", "escape DC 17"),
            ("indistinguishable from an ordinary object", "immune to all damage"),
            ("has advantage on attack rolls", "has disadvantage on attack rolls"),
        ]
        for before, after in changes:
            assert before in (card.source_actions + card.source_traits)
            altered = card.model_copy(update={
                "source_actions": card.source_actions.replace(before, after),
                "source_traits": card.source_traits.replace(before, after),
            })
            assert basic_blockers_2014(altered) != ()
        renamed = card.model_copy(update={"id": "synthetic-shapeless-beast"})
        assert proven_natural_form_only_traits_2014(renamed)
        assert source_grapple_attack_advantage_2014(renamed)
        assert original == card.model_dump_json()
    except Exception:
        logger.exception("Mimic changed source rider did not fail closed")
        raise
