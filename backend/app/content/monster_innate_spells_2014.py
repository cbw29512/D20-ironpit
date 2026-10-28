from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_innate_source_2014 import (
    ARENA_NEUTRAL_INNATE_SPELLS_2014,
    PIT_BANNED_INNATE_SPELLS_2014 as _PIT_BANNED_INNATE_SPELLS_2014,
    DISPEL_ATTACKER_TYPES_2014 as _DISPEL_ATTACKER_TYPES_2014,
    innate_spellcasting_source_2014 as _innate,
    innate_spells_2014 as _spells,
    innate_spell_save_dc_2014 as _dc,
)
from app.content.shared_control_spells_2014 import (
    blindness_deafness_2014,
    hold_monster_2014,
)
from app.content.shared_zone_spells_2014 import wall_of_fire_2014
from app.content.sorcerer_draconic_2014_spells import fireball_2014
from app.content.sorcerer_draconic_2014_spell_support import magic_missile_2014
from app.content.bard_2014_vicious_mockery import vicious_mockery_action_2014
from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.hit_effects import OnHitTimedEffect
from app.domain.persistent_save_zones import PersistentSaveZoneAction
from app.domain.debuffs import DebuffCounter
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.spells import SpellAttackAction, SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)


def innate_auto_hit_spell_actions_2014(monster: SourceMonster2014) -> list[AutoHitSpellAction]:
    """Bind printed innate auto-hit spells without monster-name dispatch."""
    try:
        return [
            magic_missile_2014()
            for spell in _spells(monster)
            if str(spell.get("id") or "") == "magic-missile"
        ]
    except Exception:
        logger.exception("Failed to compile 2014 innate auto-hit spells for %s.", monster.name)
        raise


def innate_spell_attack_actions_2014(monster: SourceMonster2014) -> list[SpellAttackAction]:
    """Bind printed innate spell attacks without monster or ability-name dispatch."""
    try:
        attack_bonus = (_innate(monster) or {}).get("attack_bonus")
        dc = _dc(monster)
        actions: list[SpellAttackAction] = []
        for spell in _spells(monster):
            if str(spell.get("id") or "") != "ray-of-enfeeblement":
                continue
            if attack_bonus is None or dc is None:
                raise ValueError(f"{monster.name} Ray of Enfeeblement lacks attack bonus or save DC.")
            actions.append(SpellAttackAction(
                id="ray-of-enfeeblement", name="Ray of Enfeeblement", level=2,
                range_ft=60, attack_bonus=int(attack_bonus),
                on_hit_modifier_effects=[SpellModifierEffect(
                    kind="weapon-attack-damage-multiplier", multiplier=0.5,
                    required_attack_ability="strength",
                )],
                on_hit_timed_effects=[OnHitTimedEffect(
                    effect_id="ray-of-enfeeblement", duration_rounds=10,
                    expiry_timing="source_turn_start", repeat_save_ability="constitution",
                    repeat_save_dc=dc, repeat_save_timing="target_turn_end",
                )],
                concentration=True, duration_minutes=1,
                animation="ray-of-enfeeblement",
                source="D&D Basic Rules 2014: Ray of Enfeeblement",
            ))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 innate spell attacks for %s.", monster.name)
        raise

def innate_spell_save_actions_2014(monster: SourceMonster2014) -> list[SpellSaveAction]:
    """Bind printed combat innate save spells. Arena-neutral spells stay source-only."""
    try:
        actions: list[SpellSaveAction] = []
        dc = _dc(monster)
        for spell in _spells(monster):
            spell_id = str(spell.get("id") or "")
            if dc is None:
                continue
            if spell_id == "entangle":
                actions.append(SpellSaveAction(
                    id="entangle",
                    name="Entangle",
                    level=1,
                    range_ft=90,
                    area=AreaTargeting(shape="cube", origin="point", length_ft=20),
                    save_ability="strength",
                    dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="restrained",
                        duration_rounds=10,
                        expiry_timing="source_turn_end",
                        escape_check_ability="strength",
                        escape_check_dc=dc,
                    ),
                    concentration=True,
                    duration_minutes=1,
                    creates_difficult_terrain=True,
                    difficult_terrain_duration_rounds=10,
                    animation="entangle",
                ))
            elif spell_id == "calm-emotions":
                actions.append(SpellSaveAction(
                    id="calm-emotions",
                    name="Calm Emotions",
                    level=2,
                    range_ft=60,
                    area=AreaTargeting(shape="radius", origin="point", radius_ft=20),
                    save_ability="charisma",
                    dc=dc,
                    required_target_creature_types=["humanoid"],
                    failed_save_modifier_effects=[
                        SpellModifierEffect(kind="condition-immunity", condition_id="charmed"),
                        SpellModifierEffect(kind="condition-immunity", condition_id="frightened"),
                        SpellModifierEffect(
                            kind="debuff-counter",
                            debuff_counter=DebuffCounter(debuff_id="charmed", source_scope="any"),
                        ),
                        SpellModifierEffect(
                            kind="debuff-counter",
                            debuff_counter=DebuffCounter(debuff_id="frightened", source_scope="any"),
                        ),
                    ],
                    concentration=True,
                    duration_minutes=1,
                    animation="calm-emotions",
                ))
            elif spell_id == "charm-person":
                actions.append(SpellSaveAction(
                    id="charm-person",
                    name="Charm Person",
                    level=1,
                    range_ft=30,
                    save_ability="wisdom",
                    dc=dc,
                    required_target_creature_types=["humanoid"],
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="charmed",
                        duration_rounds=600,
                        expiry_timing="source_turn_end",
                        ends_on_damage=True,
                    ),
                    concentration=False,
                    animation="spell-save",
                ))
            elif spell_id == "suggestion":
                actions.append(SpellSaveAction(
                    id="suggestion",
                    name="Suggestion",
                    level=2,
                    range_ft=30,
                    save_ability="wisdom",
                    dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="charmed",
                        duration_rounds=4800,
                        expiry_timing="source_turn_end",
                        ends_on_damage=True,
                    ),
                    concentration=True,
                    duration_minutes=480,
                    animation="spell-save",
                ))
            elif spell_id == "dominate-person":
                actions.append(SpellSaveAction(
                    id="dominate-person",
                    name="Dominate Person",
                    level=5,
                    range_ft=60,
                    save_ability="wisdom",
                    dc=dc,
                    required_target_creature_types=["humanoid"],
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="charmed",
                        duration_rounds=10,
                        expiry_timing="source_turn_end",
                        ends_on_damage=True,
                    ),
                    concentration=True,
                    duration_minutes=1,
                    animation="spell-save",
                ))
            elif spell_id == "hold-monster":
                actions.append(hold_monster_2014(dc))
            elif spell_id == "blindness-deafness":
                actions.append(blindness_deafness_2014(dc))
            elif spell_id == "fireball":
                actions.append(fireball_2014(dc))
            elif spell_id == "vicious-mockery":
                actions.append(vicious_mockery_action_2014(dc))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 innate save spells for %s.", monster.name)
        raise


def innate_persistent_save_zone_actions_2014(
    monster: SourceMonster2014,
) -> list[PersistentSaveZoneAction]:
    """Bind printed innate persistent zones with their own fight-local uses."""
    try:
        dc = _dc(monster)
        if dc is None:
            return []
        return [
            wall_of_fire_2014(dc).model_copy(update={"resource_id": "wall-of-fire"})
            for spell in _spells(monster)
            if str(spell.get("id") or "") == "wall-of-fire"
        ]
    except Exception:
        logger.exception("Failed to compile 2014 innate save zones for %s.", monster.name)
        raise
