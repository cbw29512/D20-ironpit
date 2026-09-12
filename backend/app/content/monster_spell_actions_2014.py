from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.domain.spells import SpellAttackAction, SpellSaveAction

SUPPORTED_DAMAGE_SPELLS_2014 = frozenset({
    "disintegrate", "fire-bolt", "fireball", "guiding-bolt",
    "inflict-wounds", "produce-flame", "sacred-flame", "shocking-grasp",
})


def _cantrip_dice(caster_level: int) -> int:
    return 1 + int(caster_level >= 5) + int(caster_level >= 11) + int(caster_level >= 17)


def _attack_spell(spell_id: str, level: int, attack_bonus: int, caster_level: int) -> SpellAttackAction:
    scaling = _cantrip_dice(caster_level)
    specs = {
        "fire-bolt": ("Fire Bolt", "ranged", 120, scaling, 10, "fire"),
        "shocking-grasp": ("Shocking Grasp", "melee", 5, scaling, 8, "lightning"),
        "produce-flame": ("Produce Flame", "ranged", 30, scaling, 8, "fire"),
        "guiding-bolt": ("Guiding Bolt", "ranged", 120, 4, 6, "radiant"),
        "inflict-wounds": ("Inflict Wounds", "melee", 5, 3, 10, "necrotic"),
    }
    name, kind, range_ft, count, size, damage_type = specs[spell_id]
    return SpellAttackAction(
        id=spell_id, name=name, level=level, attack_kind=kind, range_ft=range_ft,
        attack_bonus=attack_bonus, damage_dice_count=count, damage_dice_size=size,
        damage_type=damage_type, animation=spell_id, source="SRD 5.1 / 2014 monster spell",
    )


def _save_spell(spell_id: str, level: int, save_dc: int, caster_level: int) -> SpellSaveAction:
    if spell_id == "sacred-flame":
        return SpellSaveAction(
            id=spell_id, name="Sacred Flame", level=0, range_ft=60,
            save_ability="dexterity", dc=save_dc, damage_dice_count=_cantrip_dice(caster_level),
            damage_dice_size=8, damage_type="radiant", success_damage="none",
            animation=spell_id,
        )
    if spell_id == "fireball":
        return SpellSaveAction(
            id=spell_id, name="Fireball", level=level, range_ft=150, area_radius_ft=20,
            save_ability="dexterity", dc=save_dc, damage_dice_count=8,
            damage_dice_size=6, damage_type="fire", success_damage="half",
            upcast_dice_per_level=1, animation=spell_id,
        )
    return SpellSaveAction(
        id=spell_id, name="Disintegrate", level=level, range_ft=60,
        save_ability="dexterity", dc=save_dc, damage_dice_count=10,
        damage_dice_size=6, damage_bonus=40, damage_type="force", success_damage="none",
        upcast_dice_per_level=3, animation=spell_id,
    )


def damage_spell_actions_2014(
    source: CatalogMonster2014,
) -> tuple[list[SpellAttackAction], list[SpellSaveAction]]:
    profile = source.spellcasting
    if profile is None:
        return [], []
    attack_actions: list[SpellAttackAction] = []
    save_actions: list[SpellSaveAction] = []
    for spell in profile.spells:
        if spell.id not in SUPPORTED_DAMAGE_SPELLS_2014:
            continue
        if spell.id in {"sacred-flame", "fireball", "disintegrate"}:
            if profile.save_dc is not None:
                save_actions.append(_save_spell(spell.id, spell.level, profile.save_dc, profile.caster_level))
            continue
        if profile.attack_bonus is not None:
            attack_actions.append(_attack_spell(spell.id, spell.level, profile.attack_bonus, profile.caster_level))
    return attack_actions, save_actions
