from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.ability_check_escape import ability_check_bonus
from app.combat.ability_checks import ability_check_roll_mode, resolve_ability_check_outcome
from app.combat.condition_rules import has_condition
from app.combat.exhaustion import ability_check_disadvantage_sources, d20_modifier
from app.combat.forced_movement import pull_straight_toward, push_straight_away
from app.combat.rolls import roll_d20
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import DiceRoll, WeaponAttack
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnHitContestedMovementResolution:
    source_roll: DiceRoll | None = None
    target_roll: DiceRoll | None = None
    source_ability: str | None = None
    target_ability: str | None = None
    target_succeeded: bool | None = None
    movement_ft: int = 0
    direction: str | None = None


def _contest_disadvantage(member: EncounterCombatant, ability: str) -> int:
    return (
        ability_check_disadvantage_sources(member.state, ability)
        + int(has_condition(member.state, "poisoned") or has_condition(member.state, "frightened"))
    )


def _roll_check(member: EncounterCombatant, ability: str, dice) -> DiceRoll:
    mode = ability_check_roll_mode(
        member.state,
        disadvantage_sources=_contest_disadvantage(member, ability),
    )
    return roll_d20(
        dice,
        ability_check_bonus(member.state, ability) + d20_modifier(member.state),
        mode,
    )


def resolve_on_hit_contested_movement(
    source: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    dice,
    setup: EncounterSetup,
    *,
    round_number: int,
) -> OnHitContestedMovementResolution:
    """Resolve an opposed ability check and apply declarative forced movement on target failure."""
    try:
        effect = attack.on_hit_contested_movement
        if effect is None or target.state.is_dead or not target.state.is_alive:
            return OnHitContestedMovementResolution()
        if effect.max_target_size is not None and not size_at_most(
            target.state.template.size, effect.max_target_size
        ):
            return OnHitContestedMovementResolution()

        source_roll = _roll_check(source, effect.source_ability, dice)
        target_roll = _roll_check(target, effect.target_ability, dice)

        source_roll, _ = resolve_ability_check_outcome(
            source.state,
            effect.source_ability,
            source_roll,
            target_roll.total,
            dice=dice,
            round_number=round_number,
            encounter_roller=source,
            setup=setup,
        )
        target_roll, target_succeeded = resolve_ability_check_outcome(
            target.state,
            effect.target_ability,
            target_roll,
            source_roll.total,
            dice=dice,
            round_number=round_number,
            encounter_roller=target,
            setup=setup,
        )
        moved = 0
        if not target_succeeded:
            mover = pull_straight_toward if effect.direction == "toward_source" else push_straight_away
            moved = mover(
                target,
                source,
                setup,
                effect.distance_ft,
                round_number=round_number,
            )
        return OnHitContestedMovementResolution(
            source_roll=source_roll,
            target_roll=target_roll,
            source_ability=effect.source_ability,
            target_ability=effect.target_ability,
            target_succeeded=target_succeeded,
            movement_ft=moved,
            direction=effect.direction,
        )
    except Exception:
        logger.exception(
            "Failed contested movement rider for %s -> %s.",
            source.combatant_id,
            target.combatant_id,
        )
        raise
