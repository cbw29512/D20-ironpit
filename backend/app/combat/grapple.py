from __future__ import annotations

import logging

from app.combat.conditions import condition_state, remove_condition
from app.combat.d20_tests import resolve_ability_check, skill_modifier
from app.combat.dice import DiceProvider
from app.domain.abilities import SKILL_ABILITY, Skill
from app.domain.models import BattleEvent, CombatantState, ConditionType

logger = logging.getLogger(__name__)
_ESCAPE_SKILLS = (Skill.ATHLETICS, Skill.ACROBATICS)


def _escape_skill(state: CombatantState) -> Skill:
    return max(_ESCAPE_SKILLS, key=lambda item: (skill_modifier(state, item), -_ESCAPE_SKILLS.index(item)))


def attempt_escape_grapple(
    sequence: int,
    round_number: int,
    state: CombatantState,
    dice: DiceProvider,
) -> list[BattleEvent]:
    try:
        grapple = condition_state(state, ConditionType.GRAPPLED)
        if grapple is None:
            return []
        if not state.action_available:
            raise ValueError("Action is not available to escape Grappled.")
        if grapple.escape_dc is None:
            raise ValueError("Grappled condition is missing its escape DC.")

        state.action_available = False
        skill = _escape_skill(state)
        roll, success = resolve_ability_check(state, skill, grapple.escape_dc, dice)
        outcome = "succeeds" if success else "fails"
        events = [BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="ability_check",
            actor_id=state.instance_id,
            actor_name=state.template.name,
            target_id=grapple.source_id,
            target_name=grapple.source_name,
            ability_check=roll,
            test_dc=grapple.escape_dc,
            test_ability=SKILL_ABILITY[skill],
            test_skill=skill,
            test_success=success,
            feature_id="escape-grapple",
            animation="escape-grapple",
            description=(
                f"{state.template.name} attempts to escape Grappled with "
                f"{skill.value.title()} and {outcome}."
            ),
        )]
        if success:
            remove_condition(state, ConditionType.GRAPPLED)
            state.movement_remaining_ft = state.template.speed_ft
            events.append(BattleEvent(
                sequence=sequence + 1,
                round_number=round_number,
                event_type="condition",
                actor_id=state.instance_id,
                actor_name=state.template.name,
                target_id=state.instance_id,
                target_name=state.template.name,
                condition=ConditionType.GRAPPLED,
                condition_active=False,
                feature_id="escape-grapple",
                animation="escape-grapple-success",
                description=f"{state.template.name} ends the Grappled condition.",
            ))
        return events
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Grapple escape failed for %s.", state.template.name)
        raise RuntimeError("Grapple escape could not be resolved.") from exc
