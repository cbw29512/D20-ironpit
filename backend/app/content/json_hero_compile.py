from __future__ import annotations

import logging

from app.content.hero_combat_feature_registry import (
    compile_progression_feature_fields,
    unsupported_hero_engine_features,
)
from app.content.json_hero_attacks import compile_hero_attacks
from app.content.json_hero_derived import ability_modifier, derive_armor_class, require_matching_fingerprint
from app.domain.capabilities import CombatantDefinition
from app.domain.combatant_source import HeroBuildSource
from app.domain.traits import CombatTrait

LOGGER = logging.getLogger(__name__)
RESOURCE_ORDER = (
    "second-wind", "action-surge", "indomitable", "rage", "ki", "wholeness-of-body",
    "lay-on-hands", "channel-divinity", "spell-slot-1", "spell-slot-2", "spell-slot-3",
    "spell-slot-4", "spell-slot-5", "spell-slot-6", "spell-slot-7", "spell-slot-8",
    "spell-slot-9", "bardic-inspiration", "adrenaline-rush", "relentless-endurance",
)
TRAIT_ORDER = (CombatTrait.SAVAGE_ATTACKER, CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE)


def _ordered_resources(raw: dict[str, int]) -> list[dict[str, object]]:
    seen: list[str] = []
    for resource_id in RESOURCE_ORDER:
        if raw.get(resource_id, 0) > 0:
            seen.append(resource_id)
    for resource_id, uses in raw.items():
        if uses > 0 and resource_id not in seen:
            seen.append(resource_id)
    return [
        {
            "id": resource_id,
            "name": (
                f"Level {resource_id.rsplit('-', 1)[-1]} Spell Slot"
                if resource_id.startswith("spell-slot-")
                else resource_id.replace("-", " ").title()
            ),
            "max_uses": raw[resource_id],
        }
        for resource_id in seen
    ]


def _combat_traits(capabilities: list[str]) -> list[str]:
    available = {item.value: item for item in CombatTrait}
    traits: list[str] = []
    for trait in TRAIT_ORDER:
        if trait.value in capabilities:
            traits.append(trait.value)
    if "disciple-of-life" in capabilities and CombatTrait.LIFE_DOMAIN.value not in traits:
        traits.append(CombatTrait.LIFE_DOMAIN.value)
    for capability in capabilities:
        if capability in available and capability not in traits:
            traits.append(capability)
    return traits


def compile_hero_definition(
    hero_id: str,
    hero_name: str,
    folded: dict[str, object],
    build: HeroBuildSource,
) -> CombatantDefinition:
    try:
        if folded["edition"] != build.edition or folded["class_id"] != build.class_id:
            raise ValueError("Folded progression and hero build must share edition and class.")
        abilities = dict(folded["ability_scores"])
        proficiency = int(folded["proficiency_bonus"])
        capabilities = list(folded["capabilities"])
        edition = str(folded["edition"])
        fighting_styles = list(folded.get("fighting_styles") or [])
        if not fighting_styles and build.fighting_style:
            fighting_styles = [build.fighting_style]
        attacks = compile_hero_attacks(
            edition=edition,
            abilities=abilities,
            proficiency=proficiency,
            capabilities=capabilities,
            fighting_styles=fighting_styles,
            unarmed_dice=folded.get("unarmed_dice_size"),
            build=build,
        )
        saves = {
            ability: ability_modifier(int(score)) + (proficiency if ability in build.save_proficiencies else 0)
            for ability, score in abilities.items()
        }
        expertise = {item for item in folded.get("expertise") or []}
        skills = {}
        for skill in build.skills:
            bonus = ability_modifier(int(abilities[skill.ability]))
            if skill.proficient:
                bonus += proficiency
            if skill.id in expertise:
                bonus += proficiency
            skills[skill.id] = bonus
        initiative = ability_modifier(int(abilities["dexterity"]))
        if edition == "2014" and "remarkable-athlete" in capabilities:
            remarkable = (proficiency + 1) // 2
            initiative += remarkable
            if "acrobatics" in skills:
                skills["acrobatics"] += remarkable
        attack_count = int(folded["attack_count"])
        attack_ids = [attack.id for attack in build.attacks]
        emit_named = bool(folded.get("emit_attack_action_at_one"))
        attack_action = None
        if emit_named or attack_count > 1:
            attack_action = {
                "id": "attack" if emit_named else "extra-attack",
                "name": "Attack" if emit_named else "Extra Attack",
                "is_attack_action": True,
                "slots": [{"attack_ids": attack_ids} for _ in range(attack_count)],
            }
        progression = compile_progression_feature_fields(tuple(capabilities), int(folded["level"]), edition)
        if "tactical-master" in capabilities:
            primary = next(item for item in build.attacks if item.id == build.primary_attack_id)
            progression["tactical_master_sap_weapon_ids"] = [primary.weapon_id]
        if "survivor" in capabilities or "survivor-heroic-rally" in capabilities:
            progression["survivor_heal_amount"] = 5 + ability_modifier(int(abilities["constitution"]))
        if "intimidating-presence" in capabilities:
            progression["intimidating_presence_2014_dc"] = (
                8 + proficiency + ability_modifier(int(abilities["charisma"]))
            )
        if "sacred-weapon-2014" in capabilities:
            progression["sacred_weapon_2014_bonus"] = ability_modifier(int(abilities["charisma"]))
        if "aura-of-protection-2014" in capabilities:
            progression["aura_of_protection_2014_bonus"] = ability_modifier(int(abilities["charisma"]))
        if folded.get("unarmed_dice_size"):
            progression["martial_arts_die_size"] = int(folded["unarmed_dice_size"])
        armor_class = require_matching_fingerprint(
            "armor_class",
            derive_armor_class(
                str(build.visual.get("armor") or ""),
                abilities,
                fighting_styles,
                wielding_shield=build.visual.get("off_hand") == "shield",
                unarmored_defense_abilities=list(folded.get("unarmored_defense_abilities") or []),
                unarmored_defense_allows_shield=bool(folded.get("unarmored_defense_allows_shield")),
            ),
            folded.get("armor_class_fingerprint") if isinstance(folded.get("armor_class_fingerprint"), int) else None,
        )
        speed_ft = folded["speed_ft"] if folded.get("speed_ft") is not None else build.speed_ft
        return CombatantDefinition.model_validate({
            "schema_version": 1, "id": f"{hero_id}-l{folded['level']}", "name": hero_name,
            "archetype": build.class_id.title(), "level": folded["level"], "kind": "character",
            "ruleset": build.edition, "ability_scores": abilities, "armor_class": armor_class,
            "max_hp": folded["max_hp"], "speed_ft": speed_ft, "initiative_bonus": initiative,
            "attacks": attacks, "primary_attack_id": build.primary_attack_id,
            "attack_action": attack_action, "saving_throw_bonuses": saves, "skill_bonuses": skills,
            "combat_traits": _combat_traits(capabilities),
            "fighting_style": fighting_styles[0] if fighting_styles else build.fighting_style,
            "fighting_styles": fighting_styles, "weapon_masteries": folded["weapon_masteries"],
            "rage_damage_bonus": int(folded.get("rage_damage_bonus") or 0),
            "resources": _ordered_resources(dict(folded["resources"])), "visual": build.visual,
            "source": build.source, "progression_features": progression,
            "unsupported_capabilities": list(unsupported_hero_engine_features(tuple(capabilities))),
        })
    except Exception:
        LOGGER.exception("Failed to compile hero definition hero=%s level=%s", hero_id, folded.get("level"))
        raise
