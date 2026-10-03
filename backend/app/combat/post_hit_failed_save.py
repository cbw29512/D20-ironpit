from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.forced_movement import push_straight_away
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.content.character_math import proficiency_bonus
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import CombatantState, DiceRoll
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PostHitFailedSaveResolution:
    save_roll: DiceRoll | None
    save_ability: str
    save_dc: int
    save_succeeded: bool
    pushed_ft: int = 0
    applied_condition: str | None = None


def spell_save_dc(attacker: CombatantState, ability: str) -> int:
    """Return 8 + proficiency + the declared spellcasting ability modifier."""
    scores = attacker.template.ability_scores
    level = attacker.template.level
    if scores is None or level is None:
        raise ValueError(
            f"{attacker.template.name} post-hit save DC requires certified level and ability scores."
        )
    return 8 + proficiency_bonus(level) + scores.modifier(ability)  # type: ignore[arg-type]


def _member(setup: EncounterSetup, state: CombatantState) -> EncounterCombatant | None:
    return next(
        (member for member in [*setup.heroes, *setup.monsters] if member.state is state),
        None,
    )


def resolve_post_hit_failed_save(
    attacker: CombatantState,
    defender: CombatantState,
    dice: DiceProvider,
    setup: EncounterSetup | None,
) -> PostHitFailedSaveResolution | None:
    """Resolve a save declared by the post-hit option already paid for this hit."""
    try:
        rider = attacker.pending_post_hit_failed_save
        attacker.pending_post_hit_failed_save = None
        if rider is None:
            return None
        if defender.current_hp <= 0 or defender.is_dead or not defender.is_alive:
            return None
        dc = spell_save_dc(attacker, rider.dc_ability)
        save_roll, succeeded = resolve_saving_throw(
            defender,
            rider.save_ability,
            dc,
            dice,
            SavingThrowContext(condition_id=rider.condition_id),
        )
        applied = None
        pushed = 0
        if not succeeded:
            if (
                rider.condition_id
                and rider.condition_id not in defender.active_effect_ids
                and not condition_is_immune(
                    defender, rider.condition_id, attacker.template, source_is_magical=True,
                )
            ):
                defender.active_effect_ids.append(rider.condition_id)
                applied = rider.condition_id
            if rider.push_ft:
                if setup is None:
                    raise ValueError("Post-hit forced movement requires encounter positions.")
                source = _member(setup, attacker)
                mover = _member(setup, defender)
                if source is None or mover is None:
                    raise ValueError("Post-hit forced movement requires encounter positions.")
                pushed = push_straight_away(mover, source, setup, rider.push_ft)
        return PostHitFailedSaveResolution(
            save_roll, rider.save_ability, dc, succeeded, pushed, applied,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Post-hit failed save could not be resolved for %s.", attacker.template.name)
        raise RuntimeError("Post-hit failed save could not be resolved.") from exc
