from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.hero_combat_feature_registry import (
    compile_progression_feature_fields,
    unsupported_hero_engine_features,
)
from app.content.weapon_catalog import build_weapon
from app.domain.capabilities import CombatantDefinition
from app.domain.combatant_source import (
    HeroBuildSource,
    HeroCatalogSource,
    HeroProgressionSource,
    HeroTrackSource,
    SpeciesSource,
    SubclassProgressionSource,
)
from app.domain.traits import CombatTrait

LOGGER = logging.getLogger(__name__)
RESOURCE_ORDER = (
    "second-wind", "action-surge", "indomitable", "rage", "ki", "wholeness-of-body",
    "lay-on-hands", "channel-divinity", "spell-slot-1", "spell-slot-2", "spell-slot-3",
    "spell-slot-4", "spell-slot-5", "spell-slot-6", "spell-slot-7", "spell-slot-8",
    "spell-slot-9", "bardic-inspiration", "adrenaline-rush", "relentless-endurance",
)
TRAIT_ORDER = (
    CombatTrait.SAVAGE_ATTACKER,
    CombatTrait.ADRENALINE_RUSH,
    CombatTrait.RELENTLESS_ENDURANCE,
)


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        LOGGER.exception("Unable to read combatant source JSON path=%s", path)
        raise ValueError(f"Unable to read combatant source JSON: {path}") from exc


def load_hero_build(path: Path) -> HeroBuildSource:
    try:
        return HeroBuildSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero build path=%s", path)
        raise


def load_hero_catalog(path: Path) -> HeroCatalogSource:
    try:
        return HeroCatalogSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero catalog path=%s", path)
        raise


def load_hero_progression(path: Path) -> HeroProgressionSource:
    try:
        return HeroProgressionSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero progression path=%s", path)
        raise


def load_subclass_progression(path: Path) -> SubclassProgressionSource:
    try:
        return SubclassProgressionSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid subclass progression path=%s", path)
        raise


def load_species(path: Path) -> SpeciesSource:
    try:
        return SpeciesSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid species path=%s", path)
        raise


def load_hero_track(path: Path) -> HeroTrackSource:
    try:
        return HeroTrackSource.model_validate(_read_json(path))
    except Exception:
        LOGGER.exception("Invalid hero track path=%s", path)
        raise


def load_hero_bundle(root: Path, edition: str, slug: str):
    try:
        catalog = load_hero_catalog(root / f"data/heroes/{edition}/heroes.json")
        identity = next(item for item in catalog.heroes if item.id == slug)
        progression = load_hero_progression(
            root / f"data/heroes/{edition}/class_progressions/{identity.class_id}.json"
        )
        subclass = load_subclass_progression(
            root / f"data/heroes/{edition}/subclasses/{identity.subclass_id}.json"
        )
        species = load_species(root / f"data/heroes/{edition}/species/{identity.species}.json")
        track = load_hero_track(root / f"data/heroes/{edition}/tracks/{identity.id}.json")
        build = load_hero_build(root / f"data/heroes/{edition}/builds/{identity.id}.json")
        return identity, progression, subclass, species, track, build
    except Exception:
        LOGGER.exception("Failed to load hero bundle edition=%s slug=%s", edition, slug)
        raise


def fold_hero_level(
    progression: HeroProgressionSource,
    subclass: SubclassProgressionSource,
    species: SpeciesSource,
    track: HeroTrackSource,
    level: int,
) -> dict[str, object]:
    try:
        if progression.edition != subclass.edition or progression.class_id != subclass.class_id:
            raise ValueError("Class progression and subclass progression must share edition and class.")
        if (
            track.edition != progression.edition
            or track.class_id != progression.class_id
            or track.subclass_id != subclass.subclass_id
        ):
            raise ValueError("Hero track must share edition, class, and subclass with the progression files.")
        if species.edition != track.edition or species.id != track.species_id:
            raise ValueError("Species must share edition and id with the hero track.")
        if not 1 <= level <= len(progression.levels):
            raise ValueError(f"Requested level {level} is outside the available progression.")
        if level > len(track.hp_by_level):
            raise ValueError(f"Hero track hp_by_level does not cover level {level}.")

        capabilities: list[str] = list(species.capabilities_added)
        for item in track.origin_capabilities:
            if item not in capabilities:
                capabilities.append(item)
        ignored: list[str] = []
        resources: dict[str, int] = dict(species.resources)
        abilities = track.ability_scores.model_dump()
        proficiency = 2
        attack_count = 1
        masteries: list[str] = []
        unarmed_dice_size: int | None = None
        fighting_styles: list[str] = []
        expertise: list[str] = []

        for row in progression.levels[:level]:
            dumped = row.model_dump(exclude_none=True)
            if "proficiency_bonus" in dumped:
                proficiency = int(dumped["proficiency_bonus"])
            if "attack_count" in dumped:
                attack_count = int(dumped["attack_count"])
            if "unarmed_dice_size" in dumped:
                unarmed_dice_size = int(dumped["unarmed_dice_size"])
            resources.update(row.resources)
            capabilities = [item for item in capabilities if item not in row.capabilities_removed]
            capabilities.extend(item for item in row.capabilities_added if item not in capabilities)
            ignored.extend(item for item in row.arena_ignored if item not in ignored)

            overlay = subclass.deltas.get(row.level)
            if overlay:
                capabilities = [item for item in capabilities if item not in overlay.capabilities_removed]
                capabilities.extend(item for item in overlay.capabilities_added if item not in capabilities)
                ignored.extend(item for item in overlay.arena_ignored if item not in ignored)

            asi = track.ability_score_improvements.get(row.level)
            if asi:
                abilities.update({key: value for key, value in asi.model_dump().items() if value is not None})
            picked = track.weapon_masteries_by_level.get(row.level)
            if picked is not None:
                masteries = list(picked)
            styles = track.fighting_styles_by_level.get(row.level)
            if styles is not None:
                fighting_styles = list(styles)
            picked_expertise = track.expertise_by_level.get(row.level)
            if picked_expertise is not None:
                expertise = list(picked_expertise)

        for resource_id in species.resource_equals_proficiency:
            resources[resource_id] = proficiency

        armor_class = track.ac_by_level[level - 1] if len(track.ac_by_level) >= level else None
        speed_ft = track.speed_by_level[level - 1] if len(track.speed_by_level) >= level else None
        rage_bonus = (
            track.rage_damage_bonus_by_level[level - 1]
            if len(track.rage_damage_bonus_by_level) >= level else 0
        )
        return {
            "edition": progression.edition,
            "class_id": progression.class_id,
            "subclass_id": subclass.subclass_id,
            "species_id": species.id,
            "level": level,
            "proficiency_bonus": proficiency,
            "max_hp": track.hp_by_level[level - 1],
            "armor_class": armor_class,
            "speed_ft": speed_ft,
            "rage_damage_bonus": rage_bonus,
            "attack_count": attack_count,
            "unarmed_dice_size": unarmed_dice_size,
            "emit_attack_action_at_one": progression.emit_attack_action_at_one,
            "weapon_masteries": masteries,
            "fighting_styles": fighting_styles,
            "expertise": expertise,
            "ability_scores": abilities,
            "resources": resources,
            "capabilities": capabilities,
            "arena_ignored": ignored,
        }
    except Exception:
        LOGGER.exception(
            "Failed to fold hero progression class=%s subclass=%s species=%s level=%s",
            progression.class_id, subclass.subclass_id, species.id, level,
        )
        raise


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _catalog_weapon(weapon_id: str):
    try:
        return build_weapon(weapon_id)
    except ValueError:
        return None


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
    """Compile generic folded hero data into the same definition boundary monsters use."""
    try:
        if folded["edition"] != build.edition or folded["class_id"] != build.class_id:
            raise ValueError("Folded progression and hero build must share edition and class.")
        abilities = dict(folded["ability_scores"])
        proficiency = int(folded["proficiency_bonus"])
        capabilities = list(folded["capabilities"])
        edition = str(folded["edition"])
        gwf = "great-weapon-fighting" in capabilities
        unarmed_dice = folded.get("unarmed_dice_size")
        attacks = []
        for attack in build.attacks:
            weapon = _catalog_weapon(attack.weapon_id)
            modifier = _modifier(int(abilities[attack.ability]))
            if weapon is None:
                dice_size = int(unarmed_dice) if unarmed_dice and attack.weapon_id == "unarmed-strike" else attack.dice_size
                melee = attack.attack_kind == "melee"
                two_handed = attack.two_handed
                attacks.append({
                    "id": attack.id, "name": attack.name, "weapon_id": attack.weapon_id,
                    "attack_kind": attack.attack_kind, "attack_bonus": proficiency + modifier,
                    "damage": {"count": attack.dice_count, "size": dice_size, "bonus": modifier},
                    "damage_type": attack.damage_type, "animation": attack.animation,
                    "reach_ft": attack.reach_ft, "normal_range_ft": attack.normal_range_ft,
                    "long_range_ft": attack.long_range_ft, "mastery_property": attack.mastery_property,
                    "heavy": attack.heavy, "two_handed": two_handed,
                    "attack_ability": attack.ability, "attack_ability_modifier": modifier,
                    "rage_eligible": "rage" in capabilities,
                    "sneak_attack_eligible": "sneak-attack" in capabilities,
                    "damage_die_minimum": 3 if gwf and melee and two_handed else None,
                })
                continue
            melee = str(getattr(weapon.attack_kind, "value", weapon.attack_kind)) == "melee"
            attacks.append({
                "id": attack.id, "name": weapon.name, "weapon_id": weapon.id,
                "attack_kind": weapon.attack_kind, "attack_bonus": proficiency + modifier,
                "damage": {"count": weapon.dice_count, "size": weapon.dice_size, "bonus": modifier},
                "damage_type": weapon.damage_type, "animation": weapon.animation,
                "reach_ft": weapon.reach_ft, "normal_range_ft": weapon.normal_range_ft,
                "long_range_ft": weapon.long_range_ft, "projectile": weapon.projectile,
                "mastery_property": None if edition == "2014" else weapon.mastery_property,
                "heavy": weapon.heavy, "two_handed": weapon.two_handed,
                "light": weapon.light, "finesse": weapon.finesse, "versatile": weapon.versatile,
                "attack_ability": attack.ability, "attack_ability_modifier": modifier,
                "rage_eligible": "rage" in capabilities,
                "sneak_attack_eligible": "sneak-attack" in capabilities,
                "damage_die_minimum": 3 if gwf and melee and weapon.two_handed else None,
            })
        saves = {
            ability: _modifier(int(score)) + (proficiency if ability in build.save_proficiencies else 0)
            for ability, score in abilities.items()
        }
        expertise = {item for item in folded.get("expertise") or []}
        skills = {}
        for skill in build.skills:
            bonus = _modifier(int(abilities[skill.ability]))
            if skill.proficient:
                bonus += proficiency
            if skill.id in expertise:
                bonus += proficiency
            skills[skill.id] = bonus
        initiative = _modifier(int(abilities["dexterity"]))
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
        if "survivor" in capabilities:
            progression["survivor_heal_amount"] = 5 + _modifier(int(abilities["constitution"]))
        if "intimidating-presence" in capabilities:
            progression["intimidating_presence_2014_dc"] = (
                8 + proficiency + _modifier(int(abilities["charisma"]))
            )
        if "sacred-weapon-2014" in capabilities:
            progression["sacred_weapon_2014_bonus"] = _modifier(int(abilities["charisma"]))
        if "aura-of-protection-2014" in capabilities:
            progression["aura_of_protection_2014_bonus"] = _modifier(int(abilities["charisma"]))
        if folded.get("unarmed_dice_size"):
            progression["martial_arts_die_size"] = int(folded["unarmed_dice_size"])
        fighting_styles = list(folded.get("fighting_styles") or [])
        if not fighting_styles and build.fighting_style:
            fighting_styles = [build.fighting_style]
        armor_class = folded.get("armor_class")
        if armor_class is None:
            armor_class = build.armor_class
        speed_ft = folded.get("speed_ft")
        if speed_ft is None:
            speed_ft = build.speed_ft
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
