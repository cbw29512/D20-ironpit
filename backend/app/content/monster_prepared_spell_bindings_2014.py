"""Bind pinned 2014 monster prepared spells to existing universal actions."""
from __future__ import annotations
from dataclasses import dataclass
import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_spell_slot_resources_2014 import monster_spell_slot_resources_2014
from app.content.cleric_2014_level1_spells import (
    guiding_bolt_2014, sacred_flame_2014, inflict_wounds_2014,
    bless_2014, shield_of_faith_2014,
)
from app.content.sorcerer_draconic_2014_spell_support import (
    magic_missile_2014, shocking_grasp_2014, false_life_2014,
)
from app.content.shared_spells_2014 import (
    sanctuary_2014, aid_2014, beacon_of_hope_2014, death_ward_2014,
)
from app.content.sorcerer_draconic_2014_spells import (
    fire_bolt_2014, ray_of_frost_2014, poison_spray_2014,
    burning_hands_2014, fireball_2014, shatter_2014,
    lightning_bolt_2014, cone_of_cold_2014,
)
from app.content.shared_control_spells_2014 import hold_person_2014
from app.domain.spells import SpellAttackAction, SpellSaveAction, DefensiveSpellAction
from app.domain.auto_hit_spells import AutoHitSpellAction

logger = logging.getLogger(__name__)
# Explicitly approved noncombat choices remain on the immutable source card.
_INERT = frozenset({
    "thaumaturgy", "disguise-self", "detect-magic", "identify",
    "detect-thoughts", "scrying", "mage-hand", "prestidigitation",
})
_ATTACK_CANTRIPS = {
    "fire-bolt": fire_bolt_2014, "ray-of-frost": ray_of_frost_2014,
    "shocking-grasp": shocking_grasp_2014,
}
_SAVE_CANTRIPS = {"sacred-flame": sacred_flame_2014, "poison-spray": poison_spray_2014}
_ATTACK_SPELLS = {"guiding-bolt": guiding_bolt_2014, "inflict-wounds": inflict_wounds_2014}
_DEFENSES = {
    "bless": bless_2014, "shield-of-faith": shield_of_faith_2014,
    "false-life": false_life_2014, "aid": aid_2014,
    "beacon-of-hope": beacon_of_hope_2014, "death-ward": death_ward_2014,
}
_SAVE_SPELLS = {
    "burning-hands": burning_hands_2014, "fireball": fireball_2014,
    "shatter": shatter_2014, "lightning-bolt": lightning_bolt_2014,
    "cone-of-cold": cone_of_cold_2014, "hold-person": hold_person_2014,
}

@dataclass(frozen=True)
class PreparedSpellBindings2014:
    attacks: tuple[SpellAttackAction, ...] = ()
    saves: tuple[SpellSaveAction, ...] = ()
    auto_hits: tuple[AutoHitSpellAction, ...] = ()
    defenses: tuple[DefensiveSpellAction, ...] = ()

def _stat(source: dict, field: str, lower: int, upper: int) -> int:
    value = source.get(field)
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f"Invalid 2014 prepared spell {field}.")
    return value

def bind_prepared_spells_2014(monster: SourceMonster2014) -> PreparedSpellBindings2014:
    """Compile source IDs/levels and caster stats; never select combat by name."""
    try:
        if monster.spellcasting is None:
            return PreparedSpellBindings2014()
        monster_spell_slot_resources_2014(monster)
        source = monster.spellcasting
        attacks: list[SpellAttackAction] = []
        saves: list[SpellSaveAction] = []
        auto_hits: list[AutoHitSpellAction] = []
        defenses: list[DefensiveSpellAction] = []
        unsupported: list[str] = []
        for spell in source["spells"]:
            spell_id = spell["id"]
            if spell_id in _INERT:
                continue
            if spell_id in _ATTACK_CANTRIPS:
                result = _ATTACK_CANTRIPS[spell_id](
                    _stat(source, "attack_bonus", -20, 40),
                    _stat(source, "caster_level", 1, 20))
                attacks.append(result)
            elif spell_id in _SAVE_CANTRIPS:
                result = _SAVE_CANTRIPS[spell_id](
                    _stat(source, "save_dc", 1, 40),
                    _stat(source, "caster_level", 1, 20))
                saves.append(result)
            elif spell_id in _ATTACK_SPELLS:
                result = _ATTACK_SPELLS[spell_id](_stat(source, "attack_bonus", -20, 40))
                attacks.append(result)
            elif spell_id in _SAVE_SPELLS:
                result = _SAVE_SPELLS[spell_id](_stat(source, "save_dc", 1, 40))
                saves.append(result)
            elif spell_id in _DEFENSES:
                result = _DEFENSES[spell_id]()
                defenses.append(result)
            elif spell_id == "sanctuary":
                result = sanctuary_2014(_stat(source, "save_dc", 1, 40))
                defenses.append(result)
            elif spell_id == "magic-missile":
                result = magic_missile_2014()
                auto_hits.append(result)
            else:
                unsupported.append(spell_id)
                continue
            if result.id != spell_id or result.level != spell["level"]:
                raise ValueError(f"{monster.name}: prepared spell {spell_id} mismatches source.")
        if unsupported:
            raise ValueError(f"{monster.name}: unbound prepared spells: {', '.join(sorted(unsupported))}")
        return PreparedSpellBindings2014(tuple(attacks), tuple(saves), tuple(auto_hits), tuple(defenses))
    except Exception:
        logger.exception("Failed 2014 prepared spell binding for %s.", monster.name)
        raise
