from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.shared_control_spells_2014 import hold_person_2014, spirit_guardians_2014
from app.content.cleric_2014_level4_spells import guardian_of_faith_2014
from app.content.shared_control_spells_2014 import (
    blindness_deafness_2014,
    hold_monster_2014,
)
from app.content.cleric_2014_level1_spells import bless_2014, cure_wounds_2014, guiding_bolt_2014, inflict_wounds_2014, shield_of_faith_2014
from app.content.shared_spells_2014 import (
    sanctuary_2014, shield_2014, darkness_2014, mage_armor_2014, freedom_of_movement_2014,
    lesser_restoration_2014, counterspell_2014, gaseous_form_2014, globe_of_invulnerability_2014,
    fog_cloud_2014, calm_emotions_2014, insect_plague_2014, blade_barrier_2014,
    acid_arrow_2014, bestow_curse_2014, dominate_monster_2014, heat_metal_2014,
    power_word_kill_2014, wall_of_force_2014, fire_shield_2014, flaming_sphere_2014,
    contagion_2014,
)
from app.content.shared_restoration_spells_2014 import greater_restoration_2014
from app.content.druid_2014_level2_spells import barkskin_2014
from app.content.shared_blur_spells_2014 import blur_2014
from app.domain.actions import ConditionRemovalAction
from app.content.shared_spells_2014 import spiritual_weapon_2014
from app.domain.healing_actions import HealingAction
from app.domain.timed_self_buffs import TimedSelfBuffAction
from app.domain.spells import DefensiveSpellAction
from app.domain.movement import MovementModeGrant
from app.domain.persistent_spell_attacks import PersistentSpellAttackAction
from app.content.shared_damage_spells_2014 import (
    blight_2014, cloudkill_2014, disintegrate_2014, finger_of_death_2014,
    flame_strike_2014, harm_2014, ice_storm_2014, sacred_flame_2014, thunderwave_2014,
)
from app.content.shared_zone_spells_2014 import wall_of_fire_2014
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
from app.content.sorcerer_draconic_2014_spell_support import magic_missile_2014, shocking_grasp_2014
from app.content.bard_2014_vicious_mockery import vicious_mockery_action_2014
from app.domain.auto_hit_spells import AutoHitSpellAction
from app.domain.persistent_save_zones import PersistentSaveZoneAction
from app.domain.spells import SpellAttackAction, SpellSaveAction
from app.domain.save_effects import FailedSaveTimedEffect

logger = logging.getLogger(__name__)

# Prepared spells whose entire effect is information, cosmetic, or out-of-arena.
# Exact same policy as innate: no combat outcome under locked Pit rules.
ARENA_NEUTRAL_PREPARED_SPELLS_2014 = frozenset({
    "alarm",
    "animal-friendship",
    "animal-messenger",
    "animate-dead",
    "arcane-lock",
    "arcanists-magic-aura",
    "augury",
    "beast-sense",
    "clairvoyance",
    "commune",
    "commune-with-nature",
    "comprehend-languages",
    "contact-other-plane",
    "continual-flame",
    "control-water",
    "control-weather",
    "control-winds",
    "create-food-and-water",
    "create-or-destroy-water",
    "creation",
    "dancing-lights",
    "detect-evil-and-good",
    "detect-magic",
    "detect-poison-and-disease",
    "detect-thoughts",
    "dimension-door",
    "disguise-self",
    "divination",
    "dream",
    "druidcraft",
    "earthquake",
    "enlarge-reduce",
    "fabricate",
    "feather-fall",
    "feign-death",
    "find-the-path",
    "find-traps",
    "floating-disk",
    "geas",
    "gentle-repose",
    "glyph-of-warding",
    "goodberry",
    "guards-and-wards",
    "hallucinatory-terrain",
    "heroes-feast",
    "identify",
    "illusory-script",
    "legend-lore",
    "leomunds-secret-chest",
    "leomunds-tiny-hut",
    "levitate",
    "light",
    "locate-animals-or-plants",
    "locate-creature",
    "locate-object",
    "longstrider",
    "mage-hand",
    "magic-mouth",
    "magnificent-mansion",
    "major-image",
    "meld-into-stone",
    "mending",
    "message",
    "mind-blank",
    "minor-illusion",
    "mirage-arcane",
    "mislead",
    "misty-step",
    "mordenkainens-magnificent-mansion",
    "mordenkainens-private-sanctum",
    "move-earth",
    "nondetection",
    "nystuls-magic-aura",
    "pass-without-trace",
    "passwall",
    "plane-shift",
    "plant-growth",
    "prestidigitation",
    "private-sanctum",
    "produce-flame",
    "programmed-illusion",
    "project-image",
    "protection-from-poison",
    "purify-food-and-drink",
    "raise-dead",
    "rarys-telepathic-bond",
    "remove-curse",
    "resurrection",
    "rope-trick",
    "scrying",
    "secret-chest",
    "seeming",
    "sending",
    "shillelagh",
    "silence",
    "silent-image",
    "spare-the-dying",
    "speak-with-animals",
    "speak-with-dead",
    "speak-with-plants",
    "spike-growth",
    "stone-shape",
    "stoneskin",
    "symbol",
    "telekinesis",
    "telepathy",
    "teleport",
    "thaumaturgy",
    "time-stop",
    "tiny-hut",
    "tongues",
    "transmute-rock",
    "tree-stride",
    "true-seeing",
    "unseen-servant",
    "wall-of-thorns",
    "water-breathing",
    "water-walk",
    "wind-walk",
    "wish",
    "zone-of-truth",
})

# Conservative cantrip scaling for monsters (no character level on prepared cards).
_MONSTER_CANTRIP_LEVEL = 1


def _prepared_spells(monster: SourceMonster2014) -> list[dict[str, object]]:
    source = monster.spellcasting
    if not isinstance(source, dict) or not source.get("source_complete"):
        return []
    spells = source.get("spells") or []
    return [item for item in spells if isinstance(item, dict)]


def _save_dc(monster: SourceMonster2014) -> int | None:
    source = monster.spellcasting
    if not isinstance(source, dict):
        return None
    raw = source.get("save_dc")
    return int(raw) if raw is not None else None


def _attack_bonus(monster: SourceMonster2014) -> int | None:
    source = monster.spellcasting
    if not isinstance(source, dict):
        return None
    raw = source.get("attack_bonus")
    return int(raw) if raw is not None else None


def prepared_spell_save_actions_2014(monster: SourceMonster2014) -> list[SpellSaveAction]:
    """Bind printed prepared save spells. Highest-level damage first."""
    try:
        actions: list[SpellSaveAction] = []
        dc = _save_dc(monster)
        if dc is None:
            return actions
        for spell in _prepared_spells(monster):
            spell_id = str(spell.get("id") or "")
            # Highest-level damage first
            if spell_id == "harm":
                actions.append(harm_2014(dc))
            elif spell_id == "finger-of-death":
                actions.append(finger_of_death_2014(dc))
            elif spell_id == "disintegrate":
                actions.append(disintegrate_2014(dc))
            elif spell_id == "cloudkill":
                actions.append(cloudkill_2014(dc))
            elif spell_id == "blight":
                actions.append(blight_2014(dc))
            elif spell_id == "ice-storm":
                actions.append(ice_storm_2014(dc))
            elif spell_id == "thunderwave":
                actions.append(thunderwave_2014(dc))
            elif spell_id == "sacred-flame":
                actions.append(sacred_flame_2014(dc))
            elif spell_id == "cone-of-cold":
                actions.append(cone_of_cold_2014(dc))
            elif spell_id == "flame-strike":
                actions.append(flame_strike_2014(dc))
            elif spell_id == "lightning-bolt":
                actions.append(lightning_bolt_2014(dc))
            elif spell_id == "fireball":
                actions.append(fireball_2014(dc))
            elif spell_id == "shatter":
                actions.append(shatter_2014(dc))
            elif spell_id == "burning-hands":
                actions.append(burning_hands_2014(dc))
            elif spell_id == "poison-spray":
                actions.append(poison_spray_2014(dc, _MONSTER_CANTRIP_LEVEL))
            elif spell_id == "calm-emotions":
                dc = _save_dc(monster)
                if dc is not None:
                    actions.append(calm_emotions_2014(dc))
            elif spell_id == "insect-plague":
                actions.append(insect_plague_2014(dc))
            elif spell_id == "blade-barrier":
                actions.append(blade_barrier_2014(dc))
            elif spell_id == "bestow-curse":
                actions.append(bestow_curse_2014(dc))
            elif spell_id == "dominate-monster":
                actions.append(dominate_monster_2014(dc))
            elif spell_id == "heat-metal":
                actions.append(heat_metal_2014(dc))
            elif spell_id == "power-word-kill":
                actions.append(power_word_kill_2014())
            elif spell_id == "contagion":
                actions.append(contagion_2014(dc))
            elif spell_id == "hold-monster":
                actions.append(hold_monster_2014(dc))
            elif spell_id == "hold-person":
                actions.append(hold_person_2014(dc))
            elif spell_id == "charm-person":
                actions.append(SpellSaveAction(
                    id="charm-person", name="Charm Person", level=1, action_cost="action",
                    range_ft=30, save_ability="wisdom", dc=dc,
                    required_target_creature_types=["humanoid"],
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="charmed", duration_rounds=600,
                        expiry_timing="source_turn_end", ends_on_damage=True,
                    ),
                    animation="charm-person",
                ))
            elif spell_id == "suggestion":
                actions.append(SpellSaveAction(
                    id="suggestion", name="Suggestion", level=2, action_cost="action",
                    range_ft=30, save_ability="wisdom", dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="charmed", duration_rounds=4800,
                        expiry_timing="source_turn_end", ends_on_damage=True,
                    ),
                    concentration=True, duration_minutes=480, animation="suggestion",
                ))
            elif spell_id == "command":
                actions.append(SpellSaveAction(
                    id="command", name="Command", level=1, action_cost="action",
                    range_ft=60, save_ability="wisdom", dc=dc,
                    requires_target_sight=True,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="prone", duration_rounds=1,
                        expiry_timing="target_turn_end",
                    ),
                    animation="command",
                ))
            elif spell_id == "sleep":
                actions.append(SpellSaveAction(
                    id="sleep", name="Sleep", level=1, action_cost="action",
                    range_ft=90, save_ability="wisdom", dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="unconscious", duration_rounds=10,
                        expiry_timing="source_turn_end", ends_on_damage=True,
                    ),
                    animation="sleep",
                ))
            elif spell_id == "banishment":
                actions.append(SpellSaveAction(
                    id="banishment", name="Banishment", level=4, action_cost="action",
                    range_ft=60, save_ability="charisma", dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="banished", duration_rounds=10,
                        expiry_timing="source_turn_end",
                    ),
                    concentration=True, duration_minutes=1, animation="banishment",
                ))
            elif spell_id == "entangle":
                actions.append(SpellSaveAction(
                    id="entangle", name="Entangle", level=1, action_cost="action",
                    range_ft=90, save_ability="strength", dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="restrained", duration_rounds=10,
                        expiry_timing="source_turn_end",
                    ),
                    concentration=True, duration_minutes=1, animation="entangle",
                ))
            elif spell_id == "faerie-fire":
                actions.append(SpellSaveAction(
                    id="faerie-fire", name="Faerie Fire", level=1, action_cost="action",
                    range_ft=60, save_ability="dexterity", dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="outlined", duration_rounds=10,
                        expiry_timing="source_turn_end",
                    ),
                    concentration=True, duration_minutes=1, animation="faerie-fire",
                ))
            elif spell_id == "power-word-stun":
                actions.append(SpellSaveAction(
                    id="power-word-stun", name="Power Word Stun", level=8, action_cost="action",
                    range_ft=60, save_ability="constitution", dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="stunned", duration_rounds=10,
                        expiry_timing="source_turn_end",
                    ),
                    animation="power-word-stun",
                ))
            elif spell_id == "dominate-person":
                actions.append(SpellSaveAction(
                    id="dominate-person", name="Dominate Person", level=5, action_cost="action",
                    range_ft=60, save_ability="wisdom", dc=dc,
                    required_target_creature_types=["humanoid"],
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="charmed", duration_rounds=10,
                        expiry_timing="source_turn_end",
                    ),
                    concentration=True, duration_minutes=1, animation="dominate-person",
                ))
            elif spell_id == "confusion":
                actions.append(SpellSaveAction(
                    id="confusion", name="Confusion", level=4, action_cost="action",
                    range_ft=90, save_ability="wisdom", dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="confused", duration_rounds=10,
                        expiry_timing="source_turn_end",
                    ),
                    concentration=True, duration_minutes=1, animation="confusion",
                ))
            elif spell_id == "blindness-deafness":
                actions.append(blindness_deafness_2014(dc))
            elif spell_id == "vicious-mockery":
                actions.append(vicious_mockery_action_2014(dc))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared save spells for %s.", monster.name)
        raise


def prepared_spell_attack_actions_2014(monster: SourceMonster2014) -> list[SpellAttackAction]:
    """Bind printed prepared attack spells (cantrips)."""
    try:
        actions: list[SpellAttackAction] = []
        attack_bonus = _attack_bonus(monster)
        if attack_bonus is None:
            return actions
        for spell in _prepared_spells(monster):
            spell_id = str(spell.get("id") or "")
            if spell_id == "guiding-bolt":
                actions.append(guiding_bolt_2014(int(attack_bonus)))
            elif spell_id == "inflict-wounds":
                actions.append(inflict_wounds_2014(int(attack_bonus)))
            elif spell_id == "acid-arrow":
                actions.append(acid_arrow_2014(int(attack_bonus)))
            elif spell_id == "ray-of-enfeeblement":
                actions.append(SpellAttackAction(
                    id="ray-of-enfeeblement", name="Ray of Enfeeblement", level=2,
                    action_cost="action", attack_kind="ranged", range_ft=60,
                    attack_bonus=int(attack_bonus),
                    damage_dice_count=0, damage_dice_size=6, damage_type="necrotic",
                    animation="ray-of-enfeeblement",
                ))
            elif spell_id == "fire-bolt":
                actions.append(fire_bolt_2014(int(attack_bonus), _MONSTER_CANTRIP_LEVEL))
            elif spell_id == "ray-of-frost":
                actions.append(ray_of_frost_2014(int(attack_bonus), _MONSTER_CANTRIP_LEVEL))
            elif spell_id == "shocking-grasp":
                actions.append(shocking_grasp_2014(int(attack_bonus), _MONSTER_CANTRIP_LEVEL))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared attack spells for %s.", monster.name)
        raise


def prepared_auto_hit_spell_actions_2014(monster: SourceMonster2014) -> list[AutoHitSpellAction]:
    try:
        return [
            magic_missile_2014()
            for spell in _prepared_spells(monster)
            if str(spell.get("id") or "") == "magic-missile"
        ]
    except Exception:
        logger.exception("Failed to compile 2014 prepared auto-hit spells for %s.", monster.name)
        raise


def prepared_persistent_save_zone_actions_2014(
    monster: SourceMonster2014,
) -> list[PersistentSaveZoneAction]:
    try:
        dc = _save_dc(monster)
        if dc is None:
            return []
        return [
            wall_of_fire_2014(dc).model_copy(update={"resource_id": "wall-of-fire"})
            for spell in _prepared_spells(monster)
            if str(spell.get("id") or "") == "wall-of-fire"
        ]
    except Exception:
        logger.exception("Failed to compile 2014 prepared save zones for %s.", monster.name)
        raise


def supports_prepared_spellcasting_2014(monster: SourceMonster2014) -> bool:
    """True when every printed prepared spell is bound or arena-neutral."""
    try:
        if not monster.spellcasting:
            return True
        source = monster.spellcasting
        if not isinstance(source, dict) or not source.get("source_complete"):
            return False
        known = {str(spell.get("id") or "") for spell in _prepared_spells(monster)}
        if not known:
            return False
        bound = {
            action.id for action in prepared_spell_save_actions_2014(monster)
        } | {
            action.id for action in prepared_spell_attack_actions_2014(monster)
        } | {
            action.id for action in prepared_auto_hit_spell_actions_2014(monster)
        } | {
            action.id for action in prepared_persistent_save_zone_actions_2014(monster)
        } | {
            action.id for action in prepared_healing_spell_actions_2014(monster)
        } | {
            action.id for action in prepared_persistent_spell_attack_actions_2014(monster)
        } | {
            action.id for action in prepared_timed_self_buffs_2014(monster)
        } | {
            action.id for action in prepared_defensive_spell_actions_2014(monster)
        } | {
            action.id for action in prepared_condition_removal_actions_2014(monster)
        } | {
            action.id for action in prepared_effect_removal_actions_2014(monster)
        } | ARENA_NEUTRAL_PREPARED_SPELLS_2014
        # Arena-neutral prepared spells stay unbound by design.
        return known <= bound
    except Exception:
        logger.exception("Failed to classify 2014 prepared spellcasting for %s.", monster.name)
        raise


def prepared_healing_spell_actions_2014(monster: SourceMonster2014) -> list[HealingAction]:
    """Bind printed prepared healing spells. Ability modifier is 0 until a later explicit policy."""
    try:
        actions: list[HealingAction] = []
        for spell in _prepared_spells(monster):
            if str(spell.get("id") or "") == "cure-wounds":
                actions.append(cure_wounds_2014(0, 0))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared healing spells for %s.", monster.name)
        raise


def prepared_persistent_spell_attack_actions_2014(monster: SourceMonster2014) -> list[PersistentSpellAttackAction]:
    """Bind printed prepared persistent spell attacks."""
    try:
        actions: list[PersistentSpellAttackAction] = []
        attack_bonus = _attack_bonus(monster)
        if attack_bonus is None:
            return actions
        for spell in _prepared_spells(monster):
            if str(spell.get("id") or "") == "spiritual-weapon":
                actions.append(spiritual_weapon_2014(int(attack_bonus), 0))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared persistent spell attacks for %s.", monster.name)
        raise


def prepared_timed_self_buffs_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind printed prepared self-buffs that map to existing timed-buff primitives."""
    try:
        actions: list[TimedSelfBuffAction] = []
        for spell in _prepared_spells(monster):
            spell_id = str(spell.get("id") or "")
            if spell_id == "invisibility":
                actions.append(TimedSelfBuffAction(
                    id="invisibility", name="Invisibility", action_cost="action",
                    resource_id="invisibility", resource_cost=1, duration_rounds=600,
                    expiry_timing="source_turn_end", concentration=True,
                    condition_ids=["invisible"], animation="invisibility",
                ))
            elif spell_id == "fly":
                actions.append(TimedSelfBuffAction(
                    id="fly", name="Fly", action_cost="action",
                    resource_id="fly", resource_cost=1, duration_rounds=100,
                    expiry_timing="source_turn_end", concentration=True,
                    movement_mode_grants=[MovementModeGrant(mode="fly", fixed_speed_ft=60)],
                    animation="fly",
                ))
            elif spell_id == "darkness":
                actions.append(darkness_2014())
            # Counterspell is a Reaction, not a timed Action self-buff.
            # Leave it unbound until a generic spell-interrupt runtime is certified.
            elif spell_id == "gaseous-form":
                actions.append(gaseous_form_2014())
            elif spell_id == "globe-of-invulnerability":
                actions.append(globe_of_invulnerability_2014())
            elif spell_id == "fog-cloud":
                actions.append(fog_cloud_2014())
            elif spell_id == "wall-of-force":
                actions.append(wall_of_force_2014())
            # Fire Shield must use the shared resistance/retaliation variants
            # with source-legal spell slots; the empty placeholder is not a cast.
            elif spell_id == "spirit-guardians":
                dc = _save_dc(monster)
                if dc is not None:
                    actions.append(spirit_guardians_2014(dc))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared timed self-buffs for %s.", monster.name)
        raise


def prepared_defensive_spell_actions_2014(monster: SourceMonster2014) -> list[DefensiveSpellAction]:
    """Bind printed prepared defensive spells to existing DefensiveSpellAction primitives."""
    try:
        actions: list[DefensiveSpellAction] = []
        dc = _save_dc(monster)
        for spell in _prepared_spells(monster):
            spell_id = str(spell.get("id") or "")
            if spell_id == "blur":
                actions.append(blur_2014())
            elif spell_id == "bless":
                actions.append(bless_2014())
            elif spell_id == "shield-of-faith":
                actions.append(shield_of_faith_2014())
            elif spell_id == "shield":
                actions.append(shield_2014())
            elif spell_id == "sanctuary" and dc is not None:
                actions.append(sanctuary_2014(dc))
            elif spell_id == "barkskin":
                actions.append(barkskin_2014())
            elif spell_id == "mage-armor":
                actions.append(mage_armor_2014())
            elif spell_id == "freedom-of-movement":
                actions.append(freedom_of_movement_2014())
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared defensive spells for %s.", monster.name)
        raise


def prepared_condition_removal_actions_2014(monster: SourceMonster2014) -> list[ConditionRemovalAction]:
    """Bind printed prepared restoration spells."""
    try:
        actions: list[ConditionRemovalAction] = []
        for spell in _prepared_spells(monster):
            spell_id = str(spell.get("id") or "")
            if spell_id == "lesser-restoration":
                actions.append(lesser_restoration_2014())
            elif spell_id == "greater-restoration":
                actions.append(greater_restoration_2014())
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared condition removal for %s.", monster.name)
        raise


def prepared_effect_removal_actions_2014(monster: SourceMonster2014) -> list:
    """Bind printed prepared dispel effects."""
    try:
        from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
        actions = []
        for spell in _prepared_spells(monster):
            if str(spell.get("id") or "") == "dispel-magic":
                actions.append(dispel_magic_2014("intelligence"))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 prepared effect removal for %s.", monster.name)
        raise
