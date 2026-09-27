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
from app.domain.alternate_spell_casts import AlternateSpellCastGrant
from app.domain.area_spell_protection import AreaSpellAllyProtectionGrant
from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.models import ResourceDefinition, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures
from app.domain.spell_damage_maximizers import SpellDamageMaximizerGrant
from app.domain.spells import SpellAttackAction, SpellSaveAction

logger = logging.getLogger(__name__)
_EVOCATION_AREA_SPELL_IDS = [
    "burning-hands", "shatter", "fireball", "lightning-bolt", "cone-of-cold",
]


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


def build_wizard_evoker_features(level: int) -> ProgressionCombatFeatures:
    try:
        alternate: list[AlternateSpellCastGrant] = []
        if level >= 18:
            alternate.extend([
                AlternateSpellCastGrant(
                    source_id="spell-mastery-burning-hands",
                    source_name="Spell Mastery",
                    spell_id="burning-hands",
                    cast_level=1,
                    priority=100,
                ),
                AlternateSpellCastGrant(
                    source_id="spell-mastery-shatter",
                    source_name="Spell Mastery",
                    spell_id="shatter",
                    cast_level=2,
                    priority=100,
                ),
            ])
        if level >= 20:
            alternate.extend([
                AlternateSpellCastGrant(
                    source_id="signature-spells-fireball",
                    source_name="Signature Spells",
                    spell_id="fireball",
                    cast_level=3,
                    resource_id="signature-spell-fireball",
                    priority=90,
                ),
                AlternateSpellCastGrant(
                    source_id="signature-spells-lightning-bolt",
                    source_name="Signature Spells",
                    spell_id="lightning-bolt",
                    cast_level=3,
                    resource_id="signature-spell-lightning-bolt",
                    priority=90,
                ),
            ])
        return ProgressionCombatFeatures(
            area_spell_ally_protection=(
                AreaSpellAllyProtectionGrant(
                    source_id="sculpt-spells",
                    source_name="Sculpt Spells",
                    eligible_spell_ids=list(_EVOCATION_AREA_SPELL_IDS),
                    base_protected_allies=1,
                    protected_allies_per_slot_level=1,
                    requires_source_sight=True,
                )
                if level >= 2 else None
            ),
            alternate_spell_cast_grants=alternate,
            spell_damage_maximizer=(
                SpellDamageMaximizerGrant(
                    source_id="overchannel",
                    source_name="Overchannel",
                    eligible_spell_ids=[
                        "magic-missile", "burning-hands", "shatter",
                        "fireball", "lightning-bolt", "cone-of-cold",
                    ],
                    minimum_spell_level=1,
                    maximum_spell_level=5,
                    safe_uses=1,
                    self_damage_dice_size=12,
                    initial_self_damage_dice_per_spell_level=2,
                    self_damage_increment_per_spell_level=1,
                    self_damage_type="necrotic",
                    ignores_resistance_and_immunity=True,
                )
                if level >= 14 else None
            ),
        )
    except Exception:
        logger.exception("Failed to build Elian's 2014 progression features at level %s.", level)
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
