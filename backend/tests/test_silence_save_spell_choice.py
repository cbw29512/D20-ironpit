"""Generic spell save-casting policy must respect source verbal components in Silence."""
import logging
from unittest.mock import patch

from app.combat.spell_policy import choose_spell
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def _spell(id, verbal, score):
    return SpellSaveAction(
        id=id, name=id, level=0, action_cost="action",
        range_ft=60, save_ability="dexterity", dc=12,
        damage_dice_count=score, damage_dice_size=6,
        damage_type="fire", verbal_component=verbal,
    )


def _fixture():
    hero = build_karnok_stoneward()
    caster_template = hero.model_copy(update={
        "spell_save_actions": [
            _spell("verbal", True, 3), _spell("silent", False, 1)
        ]
    })
    caster = EncounterCombatant(
        combatant_id="caster", side="heroes", position_ft=0,
        state=build_combatant_state(caster_template),
    )
    target = EncounterCombatant(
        combatant_id="target", side="monsters", position_ft=30,
        state=build_combatant_state(hero),
    )
    return caster, EncounterSetup(
        heroes=[caster], monsters=[target],
        hero_total_levels=1, monster_total_cr="1",
    )


def test_verbal_spell_not_considered_while_silenced():
    try:
        caster, setup = _fixture()
        with patch("app.combat.spell_policy.verbal_casting_blocked", return_value=True):
            choice = choose_spell(caster, setup, "1:caster")
        assert choice is not None and choice.action.id == "silent"
        assert caster.state.action_available is True
    except Exception:
        logger.exception("Silenced save-spell selection regression failed")
        raise


def test_all_verbal_spells_unavailable_until_silence_ends():
    try:
        caster, setup = _fixture()
        caster.state.template = caster.state.template.model_copy(update={
            "spell_save_actions": [_spell("verbal", True, 3)]
        })
        with patch("app.combat.spell_policy.verbal_casting_blocked", return_value=True):
            assert choose_spell(caster, setup, "1:caster") is None
        with patch("app.combat.spell_policy.verbal_casting_blocked", return_value=False):
            result = choose_spell(caster, setup, "1:caster")
            assert result is not None and result.action.id == "verbal"
    except Exception:
        logger.exception("Silence removal save-spell selection regression failed")
        raise
