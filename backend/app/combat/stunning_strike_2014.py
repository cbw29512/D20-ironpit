from __future__ import annotations

import logging

from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.content.character_math import proficiency_bonus
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)
FEATURE_ID = "stunning-strike"
KI_RESOURCE_ID = "ki"


def _ki_resource(actor: EncounterCombatant):
    return next((item for item in actor.state.resources if item.id == KI_RESOURCE_ID), None)


def resolve_stunning_strike(
    sequence: int,
    round_number: int,
    actor: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    dice: DiceProvider,
    *,
    affected_states=None,
) -> BattleEvent | None:
    """Spend 1 Ki after a successful melee hit and apply 2014 Stunning Strike."""
    try:
        state = actor.state
        features = state.template.progression_features
        resource = _ki_resource(actor)
        if (
            state.template.ruleset != "2014"
            or not features.stunning_strike
            or attack.weapon.attack_kind is not WeaponAttackKind.MELEE
            or target.state.current_hp <= 0
            or "stunned" in target.state.active_effect_ids
            or resource is None
            or resource.current_uses <= 0
        ):
            return None
        scores = state.template.ability_scores
        level = state.template.level
        if scores is None or level is None:
            raise ValueError("Stunning Strike requires character ability scores and level.")
        resource.current_uses -= 1
        dc = 8 + proficiency_bonus(level) + scores.modifier("wisdom")
        roll, succeeded = resolve_saving_throw(target.state, "constitution", dc, dice)
        applied: list[str] = []
        if not succeeded:
            condition = apply_timed_condition(
                target.state,
                "stunned",
                actor.combatant_id,
                source_effect_id=FEATURE_ID,
                applied_round=round_number,
                expires_round=round_number + 1,
                expiry_timing="source_turn_end",
                affected_states=affected_states,
                use_default_poison_recovery=False,
            )
            if condition is not None:
                applied.append(condition)
        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=actor.combatant_id,
            actor_name=state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            saving_throw_roll=roll,
            save_ability="constitution",
            save_dc=dc,
            save_succeeded=succeeded,
            applied_condition_ids=applied,
            feature_id=FEATURE_ID,
            resource_remaining=resource.current_uses,
            animation="stun",
            description=(
                f"{state.template.name} spends 1 Ki on Stunning Strike; "
                f"{target.state.template.name} {'resists' if succeeded else 'is Stunned'}."
            ),
        )
    except Exception:
        logger.exception("Failed Stunning Strike for %s", actor.combatant_id)
        raise
