"""Bind fully source-proven Priest spells into existing 2014 shared actions.

The original prepared spell list is source data. No source-name combat
resolvers, placeholder attacks, silent spell omissions or alternate slots.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from app.content.cleric_2014_level1_spells import (
    cure_wounds_2014, guiding_bolt_2014, sacred_flame_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_priest_spellcasting_2014 import (
    source_proves_priest_spellcasting_2014,
)
from app.content.shared_control_spells_2014 import spirit_guardians_2014
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.content.shared_spells_2014 import (
    lesser_restoration_2014, sanctuary_2014, spiritual_weapon_2014,
)
from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.effect_removal import EffectRemovalAction
from app.domain.persistent_spell_attacks import PersistentSpellAttackAction
from app.domain.spells import DefensiveSpellAction, SpellAttackAction, SpellSaveAction
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreparedPriestSpellActions2014:
    """Typed source-to-capability projection; empty is fail-closed."""

    saves: tuple[SpellSaveAction, ...] = ()
    attacks: tuple[SpellAttackAction, ...] = ()
    healing: tuple[HealingAction, ...] = ()
    defenses: tuple[DefensiveSpellAction, ...] = ()
    condition_removals: tuple[ConditionRemovalAction, ...] = ()
    effect_removals: tuple[EffectRemovalAction, ...] = ()
    persistent_attacks: tuple[PersistentSpellAttackAction, ...] = ()
    timed_buffs: tuple[TimedSelfBuffAction, ...] = ()


def priest_spell_actions_2014(
    monster: SourceMonster2014,
) -> PreparedPriestSpellActions2014:
    """Compile the complete package only after printed/parsed source proof."""
    try:
        if not source_proves_priest_spellcasting_2014(monster):
            return PreparedPriestSpellActions2014()
        source = monster.spellcasting
        if not isinstance(source, dict):
            raise ValueError("Source proof returned without prepared spell data.")
        dc, attack = int(source["save_dc"]), int(source["attack_bonus"])
        level = int(source["caster_level"])
        wis = monster.abilities["wis"]
        if type(wis) is not int:
            raise ValueError("Prepared Priest Wisdom score is malformed.")
        modifier = (wis - 10) // 2
        return PreparedPriestSpellActions2014(
            saves=(sacred_flame_2014(dc, level),),
            attacks=(guiding_bolt_2014(attack),),
            healing=(cure_wounds_2014(modifier, 0),),
            defenses=(sanctuary_2014(dc),),
            condition_removals=(lesser_restoration_2014(),),
            effect_removals=(dispel_magic_2014("wisdom"),),
            persistent_attacks=(spiritual_weapon_2014(attack, modifier),),
            timed_buffs=(spirit_guardians_2014(dc),),
        )
    except Exception:
        logger.exception("Failed 2014 source-proven Priest spell compilation.")
        raise


def priest_proven_spell_ids_2014(monster: SourceMonster2014) -> set[str]:
    """Only compiled real actions plus source-proven Light/Thaumaturgy are bound."""
    try:
        if not source_proves_priest_spellcasting_2014(monster):
            return set()
        package = priest_spell_actions_2014(monster)
        return {"light", "thaumaturgy"} | {
            action.id for collection in (
                package.saves, package.attacks, package.healing,
                package.defenses, package.condition_removals,
                package.effect_removals, package.persistent_attacks,
                package.timed_buffs,
            ) for action in collection
        }
    except Exception:
        logger.exception("Failed to enumerate source-backed Priest spells.")
        raise
