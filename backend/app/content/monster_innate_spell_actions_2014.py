from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.content.shared_spell_actions_2014 import build_faerie_fire
from app.domain.actions import HitControlEffect, SavingThrowAction
from app.domain.spells import SpellSaveAction

SUPPORTED_INNATE_ACTION_SPELLS_2014 = frozenset({"blindness-deafness", "faerie-fire"})


def innate_spell_save_actions_2014(source: CatalogMonster2014) -> list[SpellSaveAction]:
    profile = source.innate_spellcasting
    if profile is None: return []
    actions: list[SpellSaveAction] = []
    for spell in profile.spells:
        if spell.id != "faerie-fire": continue
        if profile.save_dc is None: raise ValueError("Faerie Fire requires an innate spell save DC.")
        actions.append(build_faerie_fire(profile.save_dc))
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
