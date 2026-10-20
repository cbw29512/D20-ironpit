"""Shared check minimums follow battle scores; source cards stay immutable."""
import logging

from app.combat.ability_checks import apply_ability_check_minimum
from app.combat.ability_score_reduction import ABILITIES, apply_ability_score_reduction, effective_ability_score
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, resolve_escape_grapple
from app.combat.rolls import roll_d20
from app.combat.state import build_combatant_state
from app.content.barbarian_berserker_2014_runtime import build_rokhan_stonefury_2014
from app.domain.progression import AbilityCheckMinimum

logger = logging.getLogger(__name__)


def test_2014_indomitable_might_uses_live_strength_after_drain():
    try:
        base = build_rokhan_stonefury_2014(13)
        features = base.progression_features.model_copy(update={
            "ability_check_minimums": [AbilityCheckMinimum(source_id="indomitable-might", ability="strength")],
        })
        template = base.model_copy(update={"level": 18, "progression_features": features})
        state = build_combatant_state(template)
        assert effective_ability_score(state, "strength") == 20
        apply_ability_score_reduction(state, "strength", 4)
        apply_grapple(state, "monster-1", 19, 5, restrains=True)
        event = resolve_escape_grapple(1, 1, "rokhan", state, FixedDiceProvider([1]))
        # This real escape incorrectly succeeded at 20 before the existing fix.
        assert event.check_succeeded is False and event.ability_check_roll.total == 16
        assert event.ability_check_roll.revisions[-1].replacement_total == 16
        assert template.ability_scores.strength == 20
        assert effective_ability_score(build_combatant_state(template), "strength") == 20
    except Exception:
        logger.exception("The 2014 Strength check minimum ignored live score reduction.")
        raise


def test_renamed_minimum_follows_each_live_ability_and_resets():
    try:
        base = build_rokhan_stonefury_2014(13)
        original = base.model_dump_json()
        for ability in sorted(ABILITIES):
            features = base.progression_features.model_copy(update={
                "ability_check_minimums": [AbilityCheckMinimum(source_id="other-source-label", ability=ability)],
            })
            template = base.model_copy(update={"progression_features": features})
            before = template.ability_scores.score(ability)
            state = build_combatant_state(template)
            apply_ability_score_reduction(state, ability, 2)
            roll = roll_d20(FixedDiceProvider([1]), 0)
            revised = apply_ability_check_minimum(state, ability, roll)
            assert revised.total == before - 2
            assert revised.revisions[-1].source_effect_id == "other-source-label"
            assert template.ability_scores.score(ability) == before
            fresh = apply_ability_check_minimum(build_combatant_state(template), ability, roll)
            assert fresh.total == before
        assert base.model_dump_json() == original
    except Exception:
        logger.exception("A source-neutral check minimum failed live-score/rename/reset parity.")
        raise
