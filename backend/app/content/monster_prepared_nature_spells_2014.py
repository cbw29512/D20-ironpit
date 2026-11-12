"""Source-proven prepared nature spells reuse the existing 2014 Druid engine.

Schema: exact printed spell id/name/level, complete Wisdom spellcasting source,
DC, attack bonus and caster level. No monster-identity dispatch.
State: existing spell slots, Concentration, timed terrain and AC modifiers.
Shillelagh's altered weapon attack requires a separately proven active buff;
the printed powered attack is not grounds to certify it unconditionally.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.druid_2014_level1_spells import longstrider_2014, produce_flame_2014
from app.content.druid_2014_level2_spells import barkskin_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_shillelagh_2014 import source_shillelagh_buff_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.shared_nature_spells_2014 import entangle_2014, thunderwave_2014
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellSaveAction
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_KNOWN = {
    "druidcraft": ("druidcraft", 0),
    "produce-flame": ("produce flame", 0),
    "shillelagh": ("shillelagh", 0),
    "entangle": ("entangle", 1),
    "longstrider": ("longstrider", 1),
    "speak-with-animals": ("speak with animals", 1),
    "thunderwave": ("thunderwave", 1),
    "animal-messenger": ("animal messenger", 2),
    "barkskin": ("barkskin", 2),
}
_NEUTRAL = frozenset({"druidcraft", "speak-with-animals", "animal-messenger"})


@dataclass(frozen=True)
class PreparedNatureSpells2014:
    saves: tuple[SpellSaveAction, ...] = ()
    attacks: tuple[SpellAttackAction, ...] = ()
    defenses: tuple[DefensiveSpellAction, ...] = ()
    buffs: tuple[TimedSelfBuffAction, ...] = ()
    neutral_ids: frozenset[str] = frozenset()

    def implemented_ids(self) -> set[str]:
        try:
            return set(self.neutral_ids) | {
                action.id for collection in (self.saves, self.attacks, self.defenses, self.buffs)
                for action in collection
            }
        except Exception:
            logger.exception("Could not enumerate prepared 2014 nature spells.")
            raise


def prepared_nature_spells_2014(monster: SourceMonster2014) -> PreparedNatureSpells2014:
    """Bind only exact source-owned spell shapes; leave unimplemented forms blocked."""
    try:
        source = monster.spellcasting
        if (
            "Spellcasting" not in monster.trait_names
            or not isinstance(source, dict)
            or source.get("source_complete") is not True
            or not isinstance(source.get("spells"), list)
            or source.get("ability") != "wisdom"
        ):
            return PreparedNatureSpells2014()
        selected: set[str] = set()
        for spell in source["spells"]:
            if not isinstance(spell, dict):
                raise ValueError("Prepared nature spell entry is not structured.")
            spell_id = spell.get("id")
            if spell_id not in _KNOWN:
                continue
            if set(spell) != {"id", "name", "level"} or (
                spell.get("name"), spell.get("level")
            ) != _KNOWN[spell_id]:
                raise ValueError(f"Source prepared nature spell {spell_id} changed.")
            if spell_id in selected:
                raise ValueError(f"Duplicate prepared nature spell {spell_id}.")
            selected.add(spell_id)
        if not selected:
            return PreparedNatureSpells2014()
        if any(type(source.get(k)) is not int for k in (
            "caster_level", "save_dc", "attack_bonus",
        )) or not 1 <= source["caster_level"] <= 20:
            raise ValueError("Prepared nature source has invalid caster statistics.")
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Spellcasting", "").casefold()
        if "druid spells prepared" not in printed:
            raise ValueError("Prepared nature list lacks printed Druid spell source.")
        if any(
            re.search(r"\b" + re.escape(_KNOWN[spell_id][0]) + r"\b", printed) is None
            for spell_id in selected
        ):
            raise ValueError("Prepared nature spell is absent from printed source.")
        dc, attack, level = (
            source["save_dc"], source["attack_bonus"], source["caster_level"],
        )
        return PreparedNatureSpells2014(
            saves=tuple(
                action for spell_id, action in (
                    ("entangle", entangle_2014(dc)),
                    ("thunderwave", thunderwave_2014(dc)),
                ) if spell_id in selected
            ),
            attacks=(produce_flame_2014(attack, level),)
            if "produce-flame" in selected else (),
            defenses=tuple(
                action for spell_id, action in (
                    ("longstrider", longstrider_2014()),
                    ("barkskin", barkskin_2014()),
                ) if spell_id in selected
            ),
            buffs=tuple(action for action in [
                source_shillelagh_buff_2014(monster) if "shillelagh" in selected else None
            ] if action is not None),
            neutral_ids=frozenset(selected & _NEUTRAL),
        )
    except Exception:
        logger.exception("2014 prepared nature source proof failed for %s.", monster.id)
        raise
