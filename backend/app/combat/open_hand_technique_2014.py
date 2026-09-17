from __future__ import annotations

import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.content.character_math import proficiency_bonus
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)
FEATURE_ID = "open-hand-technique"


def resolve_open_hand_technique(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    target: EncounterCombatant,
    dice: DiceProvider,
) -> BattleEvent | None:
    """Use the Open Hand Technique prone option after a Flurry of Blows hit."""
    try:
        state = actor.state
        if (
            state.template.ruleset != "2014"
            or not state.template.progression_features.open_hand_technique
            or target.state.current_hp <= 0
            or "prone" in target.state.active_effect_ids
            or condition_is_immune(target.state, "prone")
        ):
            return None
        scores = state.template.ability_scores
        level = state.template.level
        if scores is None or level is None:
            raise ValueError("Open Hand Technique requires character ability scores and level.")
        dc = 8 + proficiency_bonus(level) + scores.modifier("wisdom")
        roll, succeeded = resolve_saving_throw(target.state, "dexterity", dc, dice)
        applied: list[str] = []
        if not succeeded:
            target.state.active_effect_ids.append("prone")
            applied.append("prone")
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            saving_throw_roll=roll,
            save_ability="dexterity",
            save_dc=dc,
            save_succeeded=succeeded,
            applied_condition_ids=applied,
            feature_id=FEATURE_ID,
            animation="prone",
            description=(
                f"{state.template.name} uses Open Hand Technique; "
                f"{target.state.template.name} {'keeps footing' if succeeded else 'falls Prone'}."
            ),
        )
    except Exception:
        logger.exception("Failed Open Hand Technique for %s", actor.combatant_id)
        raise
