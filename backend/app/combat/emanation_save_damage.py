from __future__ import annotations

import logging

from app.combat.damage_defenses import resolve_damage_amount
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent, DamageRollComponent, DiceRoll
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


def resolve_emanation_hit(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    target: EncounterCombatant,
    action: TimedSelfBuffAction,
    setup: EncounterSetup,
    dice: DiceProvider,
    turn_key: str,
) -> tuple[BattleEvent | None, int]:
    """Resolve one enter-or-start / turn-start emanation hit, once per turn."""
    try:
        emanation = action.start_turn_emanation_damage
        if emanation is None:
            return None, sequence
        key = f"{source.combatant_id}:{action.id}"
        if target.state.emanation_triggers_this_turn.get(key) == turn_key:
            return None, sequence
        if combatant_distance(source, target) > emanation.radius_ft:
            return None, sequence
        target.state.emanation_triggers_this_turn[key] = turn_key
        if emanation.dice_count:
            rolls = [dice.roll(emanation.dice_size) for _ in range(emanation.dice_count)]
            raw = sum(rolls)
            notation = f"{emanation.dice_count}d{emanation.dice_size}"
        else:
            rolls = []
            raw = emanation.fixed_damage
            notation = str(emanation.fixed_damage)
        succeeded = False
        save_roll = None
        if emanation.save_ability and emanation.save_dc is not None:
            save_roll, succeeded = resolve_saving_throw(
                target.state,
                emanation.save_ability,
                emanation.save_dc,
                dice,
                SavingThrowContext(magical_effect=True, spell_effect=True),
                round_number=round_number,
                encounter_roller=target,
                setup=setup,
            )
            if succeeded and emanation.success_damage == "none":
                raw = 0
            elif succeeded and emanation.success_damage == "half":
                raw //= 2
        hp_before = target.state.current_hp
        applied, absorbed_healing, absorption_source = resolve_damage_amount(raw, emanation.damage_type, target.state) if raw else (0, 0, None)
        if applied:
            apply_damage(
                target.state,
                applied,
                damage_types={emanation.damage_type},
                dice=dice,
                affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
                setup=setup,
            )
        distance = combatant_distance(source, target)
        event = BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=source.combatant_id,
            actor_name=source.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            saving_throw_roll=save_roll,
            save_ability=emanation.save_ability,
            save_dc=emanation.save_dc,
            save_succeeded=succeeded if emanation.save_ability else None,
            damage_roll=DiceRoll(notation=notation, rolls=rolls, modifier=0, total=applied),
            damage_components=[DamageRollComponent(
                source=action.name,
                notation=notation,
                rolls=rolls,
                modifier=0,
                damage_type=emanation.damage_type,
                total=raw,
                applied_total=applied,
                absorbed_healing=absorbed_healing,
                absorption_source_name=absorption_source,
            )],
            hp_before=hp_before,
            hp_after=target.state.current_hp,
            feature_id=action.id,
            animation=action.animation,
            distance_before_ft=distance,
            description=(
                f"{target.state.template.name} is caught in {source.state.template.name}'s "
                f"{action.name} and takes {applied} {emanation.damage_type.value} damage."
                + (f" {absorption_source} restores {absorbed_healing} HP." if absorption_source else "")
            ),
        )
        return event, sequence + 1
    except Exception:
        logger.exception("Emanation hit failed for %s.", target.combatant_id)
        raise
