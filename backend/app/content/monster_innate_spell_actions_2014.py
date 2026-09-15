from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.content.monster_spell_actions_2014 import _automatic_spell, _save_spell
from app.content.shared_spell_actions_2014 import build_faerie_fire
from app.domain.actions import HitControlEffect, SavingThrowAction
from app.domain.automatic_damage_spells import AutomaticDamageSpellAction
from app.domain.spells import SpellSaveAction

_INNATE_SAVE_LEVELS_2014 = {
    "cone-of-cold": 5,
    "flame-strike": 5,
    "thunderwave": 1,
}
_INNATE_AUTOMATIC_LEVELS_2014 = {
    "magic-missile": 1,
}
SUPPORTED_INNATE_ACTION_SPELLS_2014 = frozenset({
    "blindness-deafness", "faerie-fire",
    *_INNATE_SAVE_LEVELS_2014,
    *_INNATE_AUTOMATIC_LEVELS_2014,
})


def innate_spell_save_actions_2014(source: CatalogMonster2014) -> list[SpellSaveAction]:
    profile = source.innate_spellcasting
    if profile is None: return []
    actions: list[SpellSaveAction] = []
    for spell in profile.spells:
        if spell.id == "faerie-fire":
            if profile.save_dc is None: raise ValueError("Faerie Fire requires an innate spell save DC.")
            actions.append(build_faerie_fire(profile.save_dc))
            continue
        level = _INNATE_SAVE_LEVELS_2014.get(spell.id)
        if level is None: continue
        if profile.save_dc is None: raise ValueError(f"{spell.name} requires an innate spell save DC.")
        actions.append(_save_spell(spell.id, level, profile.save_dc, 1))
    return actions


def innate_automatic_damage_spell_actions_2014(source: CatalogMonster2014) -> list[AutomaticDamageSpellAction]:
    profile = source.innate_spellcasting
    if profile is None: return []
    actions: list[AutomaticDamageSpellAction] = []
    for spell in profile.spells:
        level = _INNATE_AUTOMATIC_LEVELS_2014.get(spell.id)
        if level is None: continue
        actions.append(_automatic_spell(spell.id, level))
    return actions


def innate_save_actions_2014(source: CatalogMonster2014) -> list[SavingThrowAction]:
    profile = source.innate_spellcasting
    if profile is None: return []
    actions: list[SavingThrowAction] = []
    for spell in profile.spells:
        if spell.id != "blindness-deafness": continue
        if profile.save_dc is None: raise ValueError("Blindness/Deafness requires an innate spell save DC.")
        resource_id = None if spell.usage == "at_will" else f"innate-{spell.id}"
        actions.append(SavingThrowAction(
            id=spell.id, name="Blindness/Deafness", save_ability="constitution", dc=profile.save_dc, range_ft=30,
            failure_control_effect=HitControlEffect(
                condition_id="blinded", duration_rounds=10, expiry_timing="target_turn_end",
                repeat_save_ability="constitution", repeat_save_dc=profile.save_dc, repeat_save_timing="target_turn_end",
            ),
            resource_id=resource_id, resource_cost=1, magical_effect=True, animation="blindness-deafness",
        ))
    return actions
