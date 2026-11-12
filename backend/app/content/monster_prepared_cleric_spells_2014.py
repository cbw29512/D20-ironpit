"""Source-neutral 2014 prepared Cleric spell bindings.

Data schema: source-complete list of spell IDs, names and levels plus the
caster's printed DC, attack bonus, class level, Wisdom and slot resources.
Runtime state: the existing shared spell actions, no caster identity dispatch.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from app.content.cleric_2014_level1_spells import (
    inflict_wounds_2014, sacred_flame_2014, shield_of_faith_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.shared_spells_2014 import spiritual_weapon_2014
from app.domain.persistent_spell_attacks import PersistentSpellAttackAction
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellSaveAction

logger = logging.getLogger(__name__)

# The source and level must match; names are for display, not runtime dispatch.
_KNOWN = {
    "light": ("light", 0),
    "sacred-flame": ("sacred flame", 0),
    "thaumaturgy": ("thaumaturgy", 0),
    "inflict-wounds": ("inflict wounds", 1),
    "shield-of-faith": ("shield of faith", 1),
    "spiritual-weapon": ("spiritual weapon", 2),
}
_NEUTRAL = frozenset({"light", "thaumaturgy"})


@dataclass(frozen=True)
class PreparedClericSpellActions2014:
    saves: tuple[SpellSaveAction, ...] = ()
    attacks: tuple[SpellAttackAction, ...] = ()
    defenses: tuple[DefensiveSpellAction, ...] = ()
    persistent_attacks: tuple[PersistentSpellAttackAction, ...] = ()
    neutral_ids: frozenset[str] = frozenset()

    def implemented_ids(self) -> set[str]:
        try:
            return set(self.neutral_ids) | {
                action.id for actions in (
                    self.saves, self.attacks, self.defenses, self.persistent_attacks,
                ) for action in actions
            }
        except Exception:
            logger.exception("2014 prepared Cleric spell ID enumeration failed.")
            raise


def merge_unique_spell_actions(*groups):
    """Preserve one source-owned action per spell without changing its behavior."""
    try:
        unique = {}
        for actions in groups:
            for action in actions:
                prior = unique.get(action.id)
                if prior is not None and prior != action:
                    raise ValueError(f"Conflicting prepared spell binding: {action.id}.")
                unique[action.id] = action
        return list(unique.values())
    except Exception:
        logger.exception("Generic prepared spell action merge failed.")
        raise


def prepared_cleric_spell_actions_2014(
    monster: SourceMonster2014,
) -> PreparedClericSpellActions2014:
    try:
        source = monster.spellcasting
        if (
            "Spellcasting" not in monster.trait_names
            or not isinstance(source, dict)
            or source.get("source_complete") is not True
            or not isinstance(source.get("spells"), list)
        ):
            return PreparedClericSpellActions2014()

        # Only full name/level matches may bind; a changed field fails closed.
        selected: set[str] = set()
        for spell in source["spells"]:
            if not isinstance(spell, dict):
                raise ValueError("Source prepared spell is not structured.")
            spell_id = spell.get("id")
            if spell_id not in _KNOWN:
                continue
            if set(spell) != {"id", "name", "level"} or (
                spell.get("name"), spell.get("level")
            ) != _KNOWN[spell_id]:
                raise ValueError(f"Source prepared spell {spell_id} changed.")
            if spell_id in selected:
                raise ValueError(f"Duplicate prepared spell {spell_id}.")
            selected.add(spell_id)

        if not selected:
            return PreparedClericSpellActions2014()
        if (
            type(source.get("save_dc")) is not int
            or type(source.get("attack_bonus")) is not int
            or type(source.get("caster_level")) is not int
            or not 1 <= source["caster_level"] <= 20
            or type(monster.abilities.get("wis")) is not int
        ):
            raise ValueError("Prepared Cleric spellcasting source numbers are incomplete.")
        dc, attack = source["save_dc"], source["attack_bonus"]
        caster_level = source["caster_level"]
        wisdom_mod = (monster.abilities["wis"] - 10) // 2

        # Noncombat spell names still require exact printed source membership.
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Spellcasting", "").casefold()
        neutral = frozenset(
            spell_id for spell_id in selected & _NEUTRAL
            if _KNOWN[spell_id][0] in printed
        )
        return PreparedClericSpellActions2014(
            saves=(sacred_flame_2014(dc, caster_level),)
            if "sacred-flame" in selected else (),
            attacks=(inflict_wounds_2014(attack),)
            if "inflict-wounds" in selected else (),
            defenses=(shield_of_faith_2014(),)
            if "shield-of-faith" in selected else (),
            persistent_attacks=(spiritual_weapon_2014(attack, wisdom_mod),)
            if "spiritual-weapon" in selected else (),
            neutral_ids=neutral,
        )
    except Exception:
        logger.exception("2014 prepared Cleric spell source binding failed for %s.", monster.id)
        raise
