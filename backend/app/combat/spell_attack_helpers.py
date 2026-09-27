from __future__ import annotations

from app.combat.spellcasting import slot_spell_available
from app.domain.combatants import DamageType
from app.domain.events import DamageRollComponent, DiceRoll
from app.domain.spells import SpellAttackAction


def slot_resource(caster, spell: SpellAttackAction, turn_key: str):
    if spell.level == 0 or not slot_spell_available(caster.state, turn_key):
        return None
    return next(
        (
            item for item in caster.state.resources
            if item.id == f"spell-slot-{spell.level}" and item.current_uses > 0
        ),
        None,
    )


def roll_spell_attack_damage(spell: SpellAttackAction, critical: bool, dice):
    count = spell.damage_dice_count * (2 if critical else 1)
    rolls = [dice.roll(spell.damage_dice_size) for _ in range(count)]
    total = sum(rolls) + spell.damage_bonus
    notation = f"{count}d{spell.damage_dice_size}+{spell.damage_bonus}"
    damage_type = DamageType(spell.damage_type) if spell.damage_type else None
    roll = DiceRoll(
        notation=notation, rolls=rolls, modifier=spell.damage_bonus, total=total,
    )
    if damage_type is None:
        return roll, []
    component = DamageRollComponent(
        source=spell.name,
        notation=notation,
        rolls=rolls,
        modifier=spell.damage_bonus,
        damage_type=damage_type,
        total=total,
    )
    return roll, [component]
