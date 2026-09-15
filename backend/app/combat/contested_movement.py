from __future__ import annotations

from app.combat.ability_checks import roll_ability_check
from app.combat.forced_movement import pull_toward, push_away
from app.combat.tactical_mind import apply_tactical_mind
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack
from app.domain.size import size_at_most


def apply_on_hit_contested_movement(
    attacker: EncounterCombatant,
    target: EncounterCombatant,
    attack: WeaponAttack,
    event: BattleEvent,
    setup: EncounterSetup | None,
    dice,
) -> None:
    effect = attack.on_hit_contested_movement
    if effect is None or setup is None or not event.hit or target.state.is_dead or not target.state.is_alive:
        return
    if effect.max_target_size is not None and not size_at_most(target.state.template.size, effect.max_target_size):
        return
    source_roll = roll_ability_check(attacker.state, effect.source_ability, dice)
    target_roll = roll_ability_check(target.state, effect.target_ability, dice)
    target_succeeded = target_roll.total >= source_roll.total
    tactical_used = False
    if not target_succeeded:
        target_roll, tactical_used, target_succeeded = apply_tactical_mind(
            target.state, target_roll, source_roll.total, dice,
        )
    moved = 0
    if not target_succeeded:
        mover = pull_toward if effect.direction == "toward_source" else push_away
        moved = mover(attacker, target, effect.distance_ft, setup)
    event.ability_check_roll = target_roll
    event.check_ability = effect.target_ability
    event.check_dc = source_roll.total
    event.check_succeeded = target_succeeded
    if moved:
        event.movement_ft = (event.movement_ft or 0) + moved
    tactical = " after using Tactical Mind" if tactical_used else ""
    outcome = "resists" if target_succeeded else f"is moved {moved} feet"
    event.description += (
        f" {target.state.template.name} {outcome}{tactical} in the opposed "
        f"{effect.target_ability.title()} check ({target_roll.total} vs. {source_roll.total})."
    )
