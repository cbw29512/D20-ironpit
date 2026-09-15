from __future__ import annotations

from app.domain.spell_damage import SpellDamageComponent
from app.domain.spells import SpellSaveAction

# Iron Pit favors deterministic combat over full tabletop spell simulation.
# These source spells keep their source identity but execute a simpler damaging
# spell profile of the same slot level when their printed mechanics require a
# dedicated battlefield, summon, persistent-zone, or object subsystem.
ARENA_DAMAGE_SUBSTITUTION_LEVELS_2014 = {
    "fog-cloud": 1,
    "flaming-sphere": 2,
    "heat-metal": 2,
    "levitate": 2,
    "ray-of-enfeeblement": 2,
    "spirit-guardians": 3,
    "confusion": 4,
    "guardian-of-faith": 4,
    "ice-storm": 4,
    "wall-of-fire": 4,
    "cloudkill": 5,
    "insect-plague": 5,
    "blade-barrier": 6,
    "harm": 6,
}
ARENA_DAMAGE_SUBSTITUTIONS_2014 = frozenset(ARENA_DAMAGE_SUBSTITUTION_LEVELS_2014)


def build_arena_damage_substitute(
    source_id: str,
    source_name: str,
    level: int,
    save_dc: int,
) -> SpellSaveAction:
    """Replace a complex source spell with a simple same-level arena damage spell."""
    common = dict(
        id=source_id,
        level=level,
        range_ft=60,
        dc=save_dc,
        success_damage="none" if level >= 6 else "half",
        source=f"Iron Pit arena substitution for {source_name}",
    )
    if level <= 1:
        return SpellSaveAction(
            **common, name=f"{source_name} → Thunderwave", save_ability="constitution",
            damage_dice_count=2, damage_dice_size=8, damage_type="thunder", animation="thunderwave",
        )
    if level == 2:
        return SpellSaveAction(
            **common, name=f"{source_name} → Shatter", save_ability="constitution",
            damage_dice_count=3, damage_dice_size=8, damage_type="thunder", animation="shatter",
        )
    if level == 3:
        return SpellSaveAction(
            **common, name=f"{source_name} → Fireball", save_ability="dexterity",
            damage_dice_count=8, damage_dice_size=6, damage_type="fire", animation="fireball",
        )
    if level == 4:
        return SpellSaveAction(
            **common, name=f"{source_name} → Blight", save_ability="constitution",
            damage_dice_count=8, damage_dice_size=8, damage_type="necrotic", animation="blight",
        )
    if level == 5:
        return SpellSaveAction(
            **common, name=f"{source_name} → Flame Strike", save_ability="dexterity",
            damage_dice_count=4, damage_dice_size=6, damage_type="fire",
            additional_damage_components=[SpellDamageComponent(dice_count=4, dice_size=6, damage_type="radiant")],
            animation="flame-strike",
        )
    return SpellSaveAction(
        **common, name=f"{source_name} → Disintegrate", save_ability="dexterity",
        damage_dice_count=10, damage_dice_size=6, damage_bonus=40, damage_type="force",
        animation="disintegrate",
    )
