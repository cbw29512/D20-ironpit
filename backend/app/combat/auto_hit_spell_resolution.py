from __future__ import annotations

import logging

from app.combat.action_economy import is_available, spend
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.encounter_targeting import combatant_distance
from app.combat.spellcasting import mark_slot_spell_cast, slot_spell_available
from app.combat.zero_hp import apply_damage
from app.combat.spell_damage_maximizers import maximized_auto_hit_rolls
from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.combatants import DamageType
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.spell_damage_maximizers import SpellDamageMaximizerGrant
from app.domain.events import BattleEvent, DamageRollComponent, DiceRoll

logger = logging.getLogger(__name__)


def resolve_auto_hit_spell(
    sequence: int,
    round_number: int,
    caster: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    action: AutoHitSpellAction,
    slot_level: int,
    projectile_count: int,
    turn_key: str,
    dice,
    damage_maximizer: SpellDamageMaximizerGrant | None = None,
) -> BattleEvent:
    try:
        if not is_available(caster.state, action.action_cost):
            raise ValueError(f"{action.name} cannot be cast in this action window.")
        if target.side == caster.side or target.state.is_dead or not target.state.is_alive:
            raise ValueError(f"{action.name} requires a living enemy target.")
        if combatant_distance(caster, target) > action.range_ft:
            raise ValueError(f"{action.name} target is out of range.")
        if not slot_spell_available(caster.state, turn_key):
            raise ValueError(f"A spell slot was already expended this turn.")
        resource = next(
            (item for item in caster.state.resources
             if item.id == f"spell-slot-{slot_level}" and item.current_uses > 0),
            None,
        )
        if resource is None:
            raise ValueError(f"No level {slot_level} spell slot remains for {action.name}.")

        rolls: list[int] = []
        raw_total = 0
        components: list[DamageRollComponent] = []
        maximized = (
            maximized_auto_hit_rolls(
                action.damage_dice_count, action.damage_dice_size, projectile_count,
            )
            if damage_maximizer is not None else None
        )
        for projectile in range(projectile_count):
            projectile_rolls = (
                maximized[projectile]
                if maximized is not None
                else [dice.roll(action.damage_dice_size) for _ in range(action.damage_dice_count)]
            )
            subtotal = sum(projectile_rolls) + action.damage_bonus
            rolls.extend(projectile_rolls)
            raw_total += subtotal
            components.append(DamageRollComponent(
                source=f"{action.name} projectile {projectile + 1}",
                notation=f"{action.damage_dice_count}d{action.damage_dice_size}+{action.damage_bonus}",
                rolls=projectile_rolls,
                modifier=action.damage_bonus,
                damage_type=DamageType(action.damage_type),
                total=subtotal,
            ))

        hp_before = target.state.current_hp
        temp_before = target.state.temporary_hp
        applied_total, applied_components = apply_damage_defenses(target.state, components)
        affected_states = [entry.state for entry in [*setup.heroes, *setup.monsters]]
        apply_damage(
            target.state,
            applied_total,
            damage_types={DamageType(action.damage_type)} if applied_total else set(),
            dice=dice,
            affected_states=affected_states,
            damage_components=applied_components,
        )
        mark_slot_spell_cast(caster.state, turn_key)
        resource.current_uses -= 1
        spend(caster.state, action.action_cost)

        return BattleEvent(
            sequence=sequence,
            round_number=round_number,
            event_type="feature",
            actor_id=caster.combatant_id,
            actor_name=caster.state.template.name,
            target_id=target.combatant_id,
            target_name=target.state.template.name,
            feature_id=action.id,
            damage_roll=DiceRoll(
                notation=f"{projectile_count}x({action.damage_dice_count}d{action.damage_dice_size}+{action.damage_bonus})",
                rolls=rolls,
                modifier=projectile_count * action.damage_bonus,
                total=applied_total,
            ),
            damage_components=applied_components,
            hp_before=hp_before,
            hp_after=target.state.current_hp,
            temporary_hp_before=temp_before,
            temporary_hp_after=target.state.temporary_hp,
            resource_remaining=resource.current_uses,
            animation=action.animation,
            description=(
                f"{caster.state.template.name} casts {action.name}: "
                f"{projectile_count} projectiles automatically strike {target.state.template.name}."
            ),
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Auto-hit spell failed: %s -> %s with %s.",
            caster.combatant_id, target.combatant_id, action.id,
        )
        raise RuntimeError("Auto-hit spell could not be resolved.") from exc
