from __future__ import annotations

from app.combat.damage import aggregate_damage_components, roll_damage_component
from app.combat.modifier_stack import bonus_damage_modifiers
from app.combat.spellcasting import slot_spell_available
from app.domain.combatants import DamageType
from app.domain.events import DamageRollComponent, DiceRoll
from app.domain.spells import SpellAttackAction


def cast_slot_resource(
    caster,
    spell: SpellAttackAction,
    turn_key: str,
    cast_slot_level: int | None = None,
):
    if spell.level == 0 or not slot_spell_available(caster.state, turn_key):
        return None
    level = spell.level if cast_slot_level is None else cast_slot_level
    if level < spell.level or level > 9:
        raise ValueError(f"Illegal slot level {level} for {spell.name}.")
    return next(
        (item for item in caster.state.resources
         if item.id == f"spell-slot-{level}" and item.current_uses > 0),
        None,
    )


def slot_resource(caster, spell: SpellAttackAction, turn_key: str):
    return cast_slot_resource(caster, spell, turn_key)


def roll_spell_attack_damage(
    spell: SpellAttackAction,
    critical: bool,
    dice,
    *,
    attacker=None,
    target_event_id: str | None = None,
    slot_level: int | None = None,
):
    dice_count = spell.damage_dice_count if slot_level is None else spell.damage_dice_at_slot(slot_level)
    count = dice_count * (2 if critical else 1)
    rolls = [dice.roll(spell.damage_dice_size) for _ in range(count)]
    total = sum(rolls) + spell.damage_bonus
    notation = f"{count}d{spell.damage_dice_size}+{spell.damage_bonus}"
    damage_type = DamageType(spell.damage_type) if spell.damage_type else None
    roll = DiceRoll(notation=notation, rolls=rolls, modifier=spell.damage_bonus, total=total)
    if damage_type is None:
        return roll, []
    components = [DamageRollComponent(
        source=spell.name,
        notation=notation,
        rolls=rolls,
        modifier=spell.damage_bonus,
        damage_type=damage_type,
        total=total,
    )]
    if attacker is not None:
        for modifier in bonus_damage_modifiers(attacker, target_event_id):
            components.append(roll_damage_component(
                dice,
                modifier.source_name or modifier.source_effect_id,
                modifier.dice_count,
                modifier.dice_size,
                0,
                modifier.damage_type,
                critical,
            ))
    return aggregate_damage_components(components), components
