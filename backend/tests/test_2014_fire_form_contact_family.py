"""Fire Form's contact clause reuses the same passive combat rule as Heated Body.

The movement/ignition and water clauses remain independent blockers.
"""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.melee_hit_retaliation import apply_melee_hit_retaliation
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_heated_body_2014 import fire_form_contact_retaliation_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "fire-elemental")
    except Exception:
        logger.exception("2014 Fire Elemental source was not found.")
        raise


def _test_host():
    try:
        # Fire Elemental's Touch ignition is deliberately still blocked, so
        # exercise this independent universal passive on a certified host.
        azer = next(card for card in load_monster_source_2014() if card.id == "azer")
        base = compile_combatant(adapt_basic_monster_2014(azer))
        return base.model_copy(update={
            "timed_self_buff_actions": fire_form_contact_retaliation_2014(_source()),
        })
    except Exception:
        logger.exception("Failed to prepare a certified generic passive test host.")
        raise


def test_fire_form_passive_is_compiled_but_compound_trait_stays_blocked():
    try:
        card = _source()
        original = card.model_dump_json()
        action = fire_form_contact_retaliation_2014(card)
        assert len(action) == 1
        effect = action[0]
        assert effect.name == "Fire Form"
        assert effect.activation_timing == "passive"
        assert (effect.melee_hit_retaliation.range_ft, effect.melee_hit_retaliation.dice_count,
                effect.melee_hit_retaliation.dice_size, effect.melee_hit_retaliation.damage_type.value) == (5, 1, 10, "fire")
        template = _test_host()
        assert next(a for a in template.timed_self_buff_actions if a.id == "fire-form").name == "Fire Form"
        row = template_row(template)
        serialized = next(a for a in row["timed_self_buff_actions"] if a["id"] == "fire-form")
        assert serialized["meleeHitRetaliation"] == {
            "rangeFt": 5, "diceCount": 1, "diceSize": 10,
            "damageType": "fire", "onContact": True,
        }
        assert "Fire Form" not in unsupported_traits_2014(card)
        assert "Water Susceptibility" not in unsupported_traits_2014(card)
        assert "source:trait" not in basic_blockers_2014(card)
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("Fire Form source-binding/blocked-obligation test failed.")
        raise


def test_fire_form_uses_shared_damage_defenses_and_does_not_mutate_template():
    try:
        template = _test_host()
        defender = EncounterCombatant(
            combatant_id="fire", side="monsters", position_ft=0,
            state=build_combatant_state(template),
        )
        attacker = EncounterCombatant(
            combatant_id="attacker", side="heroes", position_ft=5,
            state=build_combatant_state(build_commoner().model_copy(update={"max_hp": 100})),
        )
        assert apply_melee_hit_retaliation(
            attacker, defender, melee=True, dice=FixedDiceProvider([7]),
            affected_states=[attacker.state, defender.state],
        ) == 7
        assert attacker.state.current_hp == 93
        attacker.position_ft = 10
        assert apply_melee_hit_retaliation(
            attacker, defender, melee=True, dice=FixedDiceProvider([7]),
        ) == 0
        assert attacker.state.current_hp == 93
        assert not build_combatant_state(template).timed_effects
    except Exception:
        logger.exception("Generic Fire Form contact-damage fight test failed.")
        raise


def test_fire_form_source_mutations_fail_closed_and_identity_is_irrelevant():
    try:
        card = _source()
        renamed = card.model_copy(update={"id": "same-mechanics-different-name", "name": "Different Name"})
        assert fire_form_contact_retaliation_2014(renamed)
        for before, after in (
            ("hits it with a melee attack", "sees it with a melee attack"),
            ("within 5 feet", "within nearby feet"),
            ("1d10", "2d10"),
            ("first time it enters a creature's space", "every time it enters a creature's space"),
        ):
            altered = card.model_copy(update={
                "source_traits": card.source_traits.replace(before, after),
            })
            assert altered.source_traits != card.source_traits
            assert not fire_form_contact_retaliation_2014(altered)
    except Exception:
        logger.exception("Fire Form source mutation contract failed.")
        raise
