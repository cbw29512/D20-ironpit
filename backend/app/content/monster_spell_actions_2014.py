from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.content.shared_spell_actions_2014 import build_faerie_fire
from app.domain.automatic_damage_spells import AutomaticDamageSpellAction
from app.domain.spell_damage import SpellDamageComponent
from app.domain.spells import SpellAttackAction, SpellModifierEffect, SpellSaveAction
from app.domain.targeting import AreaTargeting

SUPPORTED_DAMAGE_SPELLS_2014 = frozenset({
    "blight", "cone-of-cold", "disintegrate", "faerie-fire", "finger-of-death", "fire-bolt", "fireball", "flame-strike", "guiding-bolt",
    "inflict-wounds", "lightning-bolt", "magic-missile", "power-word-kill", "produce-flame",
    "ray-of-frost", "sacred-flame", "shocking-grasp", "thunderwave",
})
SPELL_TARGET_RULES_2014 = {
    "blight": {
        "excluded_creature_types": ["undead", "construct"],
        "save_disadvantage_creature_types": ["plant"],
        "maximize_damage_creature_types": ["plant"],
    },
}


def _cantrip_dice(caster_level: int) -> int:
    return 1 + int(caster_level >= 5) + int(caster_level >= 11) + int(caster_level >= 17)


def _attack_spell(spell_id: str, level: int, attack_bonus: int, caster_level: int) -> SpellAttackAction:
    scaling = _cantrip_dice(caster_level)
    specs = {
        "fire-bolt": ("Fire Bolt", "ranged", 120, scaling, 10, "fire"),
        "shocking-grasp": ("Shocking Grasp", "melee", 5, scaling, 8, "lightning"),
        "produce-flame": ("Produce Flame", "ranged", 30, scaling, 8, "fire"),
        "ray-of-frost": ("Ray of Frost", "ranged", 60, scaling, 8, "cold"),
        "guiding-bolt": ("Guiding Bolt", "ranged", 120, 4, 6, "radiant"),
        "inflict-wounds": ("Inflict Wounds", "melee", 5, 3, 10, "necrotic"),
    }
    name, kind, range_ft, count, size, damage_type = specs[spell_id]
    modifiers = []
    if spell_id == "ray-of-frost": modifiers.append(SpellModifierEffect(kind="speed", flat_bonus=-10, expires_at_start_of_source_turn=True))
    return SpellAttackAction(
        id=spell_id, name=name, level=level, attack_kind=kind, range_ft=range_ft,
        attack_bonus=attack_bonus, damage_dice_count=count, damage_dice_size=size,
        damage_type=damage_type, on_hit_modifier_effects=modifiers,
        animation=spell_id, source="SRD 5.1 / 2014 monster spell",
    )


def _save_spell(spell_id: str, level: int, save_dc: int, caster_level: int) -> SpellSaveAction:
    if spell_id == "faerie-fire": return build_faerie_fire(save_dc)
    if spell_id == "sacred-flame":
        return SpellSaveAction(
            id=spell_id, name="Sacred Flame", level=0, range_ft=60,
            save_ability="dexterity", dc=save_dc, damage_dice_count=_cantrip_dice(caster_level),
            damage_dice_size=8, damage_type="radiant", success_damage="none", animation=spell_id,
        )
    if spell_id == "finger-of-death":
        return SpellSaveAction(
            id=spell_id, name="Finger of Death", level=7, range_ft=60,
            save_ability="constitution", dc=save_dc, damage_dice_count=7,
            damage_dice_size=8, damage_bonus=30, damage_type="necrotic", success_damage="half",
            animation=spell_id,
        )
    if spell_id == "flame-strike":
        return SpellSaveAction(
            id=spell_id, name="Flame Strike", level=5, range_ft=60, area_radius_ft=10,
            save_ability="dexterity", dc=save_dc, damage_dice_count=4,
            damage_dice_size=6, damage_type="fire",
            additional_damage_components=[SpellDamageComponent(dice_count=4, dice_size=6, damage_type="radiant")],
            success_damage="half", animation=spell_id,
        )
    if spell_id == "fireball":
        return SpellSaveAction(
            id=spell_id, name="Fireball", level=level, range_ft=150, area_radius_ft=20,
            save_ability="dexterity", dc=save_dc, damage_dice_count=8,
            damage_dice_size=6, damage_type="fire", success_damage="half",
            upcast_dice_per_level=1, animation=spell_id,
        )
    if spell_id == "blight":
        return SpellSaveAction(
            id=spell_id, name="Blight", level=level, range_ft=30,
            save_ability="constitution", dc=save_dc, damage_dice_count=8,
            damage_dice_size=8, damage_type="necrotic", success_damage="half",
            upcast_dice_per_level=1, animation=spell_id, **SPELL_TARGET_RULES_2014[spell_id],
        )
    if spell_id == "cone-of-cold":
        return SpellSaveAction(
            id=spell_id, name="Cone of Cold", level=level, range_ft=0,
            area=AreaTargeting(shape="cone", origin="self", length_ft=60),
            save_ability="constitution", dc=save_dc, damage_dice_count=8,
            damage_dice_size=8, damage_type="cold", success_damage="half",
            upcast_dice_per_level=1, animation=spell_id,
        )
    if spell_id == "lightning-bolt":
        return SpellSaveAction(
            id=spell_id, name="Lightning Bolt", level=level, range_ft=0,
            area=AreaTargeting(shape="line", origin="self", length_ft=100, width_ft=5),
            save_ability="dexterity", dc=save_dc, damage_dice_count=8,
            damage_dice_size=6, damage_type="lightning", success_damage="half",
            upcast_dice_per_level=1, animation=spell_id,
        )
    if spell_id == "thunderwave":
        return SpellSaveAction(
            id=spell_id, name="Thunderwave", level=level, range_ft=0,
            area=AreaTargeting(shape="cube", origin="self", length_ft=15),
            save_ability="constitution", dc=save_dc, damage_dice_count=2,
            damage_dice_size=8, damage_type="thunder", success_damage="half",
            failure_push_ft=10, upcast_dice_per_level=1, animation=spell_id,
        )
    return SpellSaveAction(
        id=spell_id, name="Disintegrate", level=level, range_ft=60,
        save_ability="dexterity", dc=save_dc, damage_dice_count=10,
        damage_dice_size=6, damage_bonus=40, damage_type="force", success_damage="none",
        upcast_dice_per_level=3, animation=spell_id,
    )


def _automatic_spell(spell_id: str, level: int) -> AutomaticDamageSpellAction:
    if spell_id == "power-word-kill":
        return AutomaticDamageSpellAction(
            id=spell_id, name="Power Word Kill", level=9, range_ft=60,
            instant_death_hp_threshold=100, animation=spell_id,
            source="SRD 5.1 / 2014 monster spell",
        )
    if spell_id != "magic-missile": raise ValueError(f"Unsupported automatic spell: {spell_id}")
    return AutomaticDamageSpellAction(
        id="magic-missile", name="Magic Missile", level=level, range_ft=120,
        base_projectiles=3, damage_dice_count_per_projectile=1,
        damage_dice_size=4, damage_bonus_per_projectile=1, damage_type="force",
        animation="magic-missile", source="SRD 5.1 / 2014 monster spell",
    )


def damage_spell_actions_2014(source: CatalogMonster2014) -> tuple[list[SpellAttackAction], list[SpellSaveAction], list[AutomaticDamageSpellAction]]:
    attack_actions: list[SpellAttackAction] = []
    save_actions: list[SpellSaveAction] = []
    automatic_actions: list[AutomaticDamageSpellAction] = []
    profile = source.spellcasting
    save_ids = {"blight", "sacred-flame", "fireball", "disintegrate", "cone-of-cold", "finger-of-death", "flame-strike", "lightning-bolt", "thunderwave", "faerie-fire"}
    automatic_ids = {"magic-missile", "power-word-kill"}
    if profile is not None:
        for spell in profile.spells:
            if spell.id not in SUPPORTED_DAMAGE_SPELLS_2014: continue
            if spell.id in automatic_ids:
                automatic_actions.append(_automatic_spell(spell.id, spell.level)); continue
            if spell.id in save_ids:
                if profile.save_dc is not None: save_actions.append(_save_spell(spell.id, spell.level, profile.save_dc, profile.caster_level))
                continue
            if profile.attack_bonus is not None: attack_actions.append(_attack_spell(spell.id, spell.level, profile.attack_bonus, profile.caster_level))
    innate = source.innate_spellcasting
    if innate is not None and any(spell.id == "magic-missile" for spell in innate.spells):
        automatic_actions.append(_automatic_spell("magic-missile", 1))
    return attack_actions, save_actions, automatic_actions
