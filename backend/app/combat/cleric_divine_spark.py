from __future__ import annotations

from app.combat.auras import roll_advantage_sources
from app.combat.damage_defenses import adjusted_damage_amount, apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.zero_hp import apply_damage, restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll

DIVINE_SPARK = "divine-spark"


def _damage_type(target: EncounterCombatant) -> DamageType:
    radiant = adjusted_damage_amount(2, DamageType.RADIANT, target.state)
    necrotic = adjusted_damage_amount(2, DamageType.NECROTIC, target.state)
    return DamageType.RADIANT if radiant >= necrotic else DamageType.NECROTIC


def _wisdom_modifier(cleric: EncounterCombatant, save_dc: int) -> int:
    level = cleric.state.template.level or 1
    proficiency = 2 + (level - 1) // 4
    return save_dc - 8 - proficiency


def resolve_divine_spark(
    sequence: int,
    round_number: int,
    cleric: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    *,
    healing: bool,
    save_dc: int,
    resource_remaining: int,
) -> BattleEvent:
    if target.combatant_id == cleric.combatant_id or abs(cleric.position_ft - target.position_ft) > 30:
        raise ValueError("Divine Spark requires another creature within 30 feet.")
    roll = dice.roll(8)
    modifier = _wisdom_modifier(cleric, save_dc)
    total = roll + modifier
    notation = f"1d8+{modifier}"
    if healing:
        before = target.state.current_hp
        healed = restore_hit_points(target.state, total)
        return BattleEvent(
            sequence=sequence, round_number=round_number, event_type="healing",
            actor_id=cleric.combatant_id, actor_name=cleric.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            healing_roll=DiceRoll(notation=notation, rolls=[roll], modifier=modifier, total=total),
            hp_before=before, hp_after=target.state.current_hp, feature_id=DIVINE_SPARK,
            resource_remaining=resource_remaining, animation="divine-spark",
            description=f"{cleric.state.template.name} restores {healed} HP with Divine Spark.",
        )
    save_advantage = roll_advantage_sources(target, setup, "saving_throw")
    save, succeeded = resolve_saving_throw(
        target.state, "constitution", save_dc, dice, advantage_sources=save_advantage,
    )
    damage_type = _damage_type(target)
    component = DamageRollComponent(
        source="Divine Spark", notation=notation, rolls=[roll], modifier=modifier,
        damage_type=damage_type, total=total // 2 if succeeded else total,
    )
    applied_total, components = apply_damage_defenses(target.state, [component])
    before = target.state.current_hp
    if applied_total:
        states = [member.state for member in [*setup.heroes, *setup.monsters]]
        apply_damage(
            target.state, applied_total, damage_types={damage_type}, dice=dice, affected_states=states,
            saving_throw_advantage_sources=save_advantage,
        )
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="saving_throw",
        actor_id=cleric.combatant_id, actor_name=cleric.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name,
        saving_throw_roll=save, save_ability="constitution", save_dc=save_dc, save_succeeded=succeeded,
        damage_roll=DiceRoll(notation=notation, rolls=[roll], modifier=modifier, total=applied_total),
        damage_components=components, hp_before=before, hp_after=target.state.current_hp,
        feature_id=DIVINE_SPARK, resource_remaining=resource_remaining, animation="divine-spark",
        description=f"{target.state.template.name} takes {applied_total} {damage_type.value} damage from Divine Spark.",
    )
