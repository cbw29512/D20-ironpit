from __future__ import annotations

import logging
from dataclasses import dataclass

from app.content.character_math import proficiency_bonus
from app.content.sorcerer_draconic_2014_spell_support import magic_missile_2014, shocking_grasp_2014
from app.content.sorcerer_draconic_2014_spells import (
    burning_hands_2014,
    cone_of_cold_2014,
    fire_bolt_2014,
    fireball_2014,
    lightning_bolt_2014,
    poison_spray_2014,
    ray_of_frost_2014,
    shatter_2014,
)
from app.content.weapon_catalog import build_weapon
from app.content.wizard_evoker_2014_features import build_wizard_evoker_features
from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.models import ResourceDefinition, WeaponAttack
from app.domain.spells import SpellAttackAction, SpellSaveAction

logger = logging.getLogger(__name__)
@dataclass(frozen=True)
class WizardEvoker2014SpellActions:
    attacks: list[SpellAttackAction]
    auto_hits: list[AutoHitSpellAction]
    saves: list[SpellSaveAction]


def build_wizard_weapon(level: int, scores) -> WeaponAttack:
    try:
        weapon = build_weapon("dagger").model_copy(update={"mastery_property": None})
        dexterity = scores.modifier("dexterity")
        return WeaponAttack(
            id="elian-2014-dagger",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build Elian's 2014 dagger at level %s.", level)
        raise


def build_wizard_spell_actions(
    level: int,
    spell_attack_bonus: int,
    save_dc: int,
    intelligence_modifier: int,
) -> WizardEvoker2014SpellActions:
    try:
        empowered = intelligence_modifier if level >= 10 else 0
        poison = poison_spray_2014(save_dc, level)
        if level >= 6:
            poison = poison.model_copy(update={"success_damage": "half"})

        missile = magic_missile_2014()
        if level >= 10:
            missile = missile.model_copy(
                update={"damage_bonus": missile.damage_bonus + intelligence_modifier}
            )

        ray = ray_of_frost_2014(spell_attack_bonus, level)
        grasp = shocking_grasp_2014(spell_attack_bonus, level)
        shatter = shatter_2014(save_dc)
        cone = cone_of_cold_2014(save_dc)
        lightning = lightning_bolt_2014(save_dc)
        if level >= 10:
            ray = ray.model_copy(update={"damage_bonus": intelligence_modifier})
            grasp = grasp.model_copy(update={"damage_bonus": intelligence_modifier})
            shatter = shatter.model_copy(update={"damage_bonus": intelligence_modifier})
            cone = cone.model_copy(update={"damage_bonus": intelligence_modifier})
            lightning = lightning.model_copy(update={"damage_bonus": intelligence_modifier})

        return WizardEvoker2014SpellActions(
            attacks=[
                fire_bolt_2014(spell_attack_bonus, level, empowered),
                ray,
                *([grasp] if level >= 4 else []),
            ],
            auto_hits=[missile],
            saves=[
                poison,
                burning_hands_2014(save_dc, empowered),
                *([shatter] if level >= 3 else []),
                *([fireball_2014(save_dc, empowered)] if level >= 5 else []),
                *([cone] if level >= 9 else []),
                *([lightning] if level >= 20 else []),
            ],
        )
    except Exception:
        logger.exception("Failed to build Elian's 2014 spell actions at level %s.", level)
        raise


def build_wizard_resources(
    spell_slots: tuple[int, int, int, int, int, int, int, int, int],
    level: int,
) -> list[ResourceDefinition]:
    try:
        resources = [
            ResourceDefinition(
                id=f"spell-slot-{spell_level}",
                name=f"Spell Slot {spell_level}",
                max_uses=uses,
            )
            for spell_level, uses in enumerate(spell_slots, start=1)
            if uses
        ]
        if level >= 20:
            resources.extend([
                ResourceDefinition(
                    id="signature-spell-fireball",
                    name="Signature Spells: Fireball",
                    max_uses=1,
                ),
                ResourceDefinition(
                    id="signature-spell-lightning-bolt",
                    name="Signature Spells: Lightning Bolt",
                    max_uses=1,
                ),
            ])
        return resources
    except Exception:
        logger.exception("Failed to build Elian's 2014 resources at level %s.", level)
        raise
