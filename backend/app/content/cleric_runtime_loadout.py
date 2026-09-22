from __future__ import annotations

from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS
from app.content.cleric_life_domain import disciple_of_life_bonus
from app.content.healing_spell_effects import (
    build_cure_wounds,
    build_healing_word,
    build_mass_cure_wounds,
    build_mass_healing_word,
)
from app.content.offensive_spell_effects import build_inflict_wounds, build_sacred_flame
from app.domain.actions import HealingAction
from app.domain.combatants import ResourceDefinition
from app.domain.spells import SpellSaveAction


def build_seraphine_resources(level: int) -> list[ResourceDefinition]:
    row = CLERIC_COMBAT_LEVELS[level]
    resources = [
        ResourceDefinition(
            id=f"spell-slot-{spell_level}",
            name=f"Level {spell_level} Spell Slot",
            max_uses=uses,
        )
        for spell_level, uses in enumerate(row.spell_slots, start=1)
        if uses
    ]
    if row.channel_divinity_uses:
        resources.append(ResourceDefinition(
            id="channel-divinity",
            name="Channel Divinity",
            max_uses=row.channel_divinity_uses,
        ))
    if level >= 10:
        resources.append(ResourceDefinition(
            id="divine-intervention",
            name="Divine Intervention",
            max_uses=1,
        ))
    resources.extend((
        ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=row.proficiency_bonus),
        ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
    ))
    return resources


def build_seraphine_healing(
    level: int,
    wisdom_modifier: int,
    features: tuple[str, ...],
) -> list[HealingAction]:
    life = "disciple-of-life" in features
    actions = [build_cure_wounds(wisdom_modifier, disciple_of_life_bonus(1) if life else 0)]
    if level >= 2:
        actions.append(build_healing_word(wisdom_modifier, disciple_of_life_bonus(1) if life else 0))
    if level >= 5:
        actions.append(build_mass_healing_word(
            wisdom_modifier, disciple_of_life_bonus(3) if life else 0,
        ))
    if level >= 9:
        actions.append(build_mass_cure_wounds(
            wisdom_modifier, disciple_of_life_bonus(5) if life else 0,
        ))
    if level >= 11:
        actions.append(build_mass_cure_wounds(
            wisdom_modifier, disciple_of_life_bonus(6) if life else 0, 6,
        ))
    return actions


def build_seraphine_save_spells(
    level: int,
    save_dc: int,
    wisdom_modifier: int,
    features: tuple[str, ...],
) -> list[SpellSaveAction]:
    spells = [build_sacred_flame(
        save_dc,
        level,
        wisdom_modifier if "blessed-strikes" in features else 0,
    )]
    if level >= 4:
        spells.append(build_inflict_wounds(save_dc))
    if level >= 9:
        spells.append(build_inflict_wounds(save_dc, 5))
    if level >= 11:
        spells.append(build_inflict_wounds(save_dc, 6))
    return spells


def seraphine_source(level: int) -> str:
    milestones = (
        (2, "Healing Word, Channel Divinity, "),
        (3, "Life Domain, Aid, Lesser Restoration, Disciple of Life, "),
        (4, "Ability Score Improvement, Mending, Inflict Wounds, "),
        (5, "Sear Undead, Mass Healing Word, Revivify, Dispel Magic, "),
        (6, "Blessed Healer, "),
        (7, "Blessed Strikes, Aura of Life, Death Ward, Prayer of Healing, "),
        (8, "Guardian of Faith, Ability Score Improvement, "),
        (9, "Greater Restoration, Mass Cure Wounds, Flame Strike, Insect Plague, "),
        (10, "Divine Intervention, Contagion, Spare the Dying, "),
        (11, "Heal, sixth-level Inflict Wounds and Mass Cure Wounds upcasts, "),
    )
    details = "".join(text for minimum, text in milestones if level >= minimum)
    return (
        f"D&D Beyond Basic Rules 2024: Cleric level {level}, Orc, Sage, Protector, "
        f"Sacred Flame, Bless, Cure Wounds, Guiding Bolt, Shield of Faith, {details}Equipment"
    )
