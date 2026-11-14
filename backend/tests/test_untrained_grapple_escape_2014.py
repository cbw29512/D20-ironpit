"""Universal Grapple escape falls back to source ability scores for untrained checks."""
import logging

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.domain.encounters import EncounterSelection

logger = logging.getLogger(__name__)


def test_2014_animated_armor_untrained_escape_is_legal():
    try:
        setup = build_encounter_setup(EncounterSelection(
            ruleset="2014",
            hero_ids=["thalen-greenbough-2014-l4"],
            monster_ids=["2014-animated-armor"],
        ))
        hero, armor = setup.heroes[0], setup.monsters[0]
        state = armor.state
        snapshot = state.template.model_dump_json()
        scores = state.template.ability_scores
        assert scores is not None
        assert "athletics" not in state.template.skill_bonuses
        assert "acrobatics" not in state.template.skill_bonuses
        expected = max(scores.modifier("strength"), scores.modifier("dexterity"))
        apply_grapple(state, hero.combatant_id, 10, 5, restrains=True)
        event = resolve_escape_grapple(
            1, 1, armor.combatant_id, state, FixedDiceProvider([20]),
            encounter_actor=armor, setup=setup,
        )
        assert event.feature_id == "escape-grapple"
        assert event.check_succeeded is True
        assert event.ability_check_roll.modifier == expected
        assert not state.action_available
        assert not state.grapple_sources
        assert state.template.model_dump_json() == snapshot
    except Exception:
        logger.exception("2014 untrained Grapple escape did not use source ability scores")
        raise
