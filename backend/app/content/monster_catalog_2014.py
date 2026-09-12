from __future__ import annotations

import json
import logging
from pathlib import Path

from pydantic import TypeAdapter

from app.content.monster_catalog_2014_models import CatalogAttack2014, CatalogMonster2014
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.movement import MovementModes

logger = logging.getLogger(__name__)
CATALOG_ROOT = Path(__file__).resolve().parents[3] / "data" / "monsters" / "2014"
_MONSTERS = TypeAdapter(list[CatalogMonster2014])
_ABILITY_NAMES = {
    "str": "strength", "dex": "dexterity", "con": "constitution",
    "int": "intelligence", "wis": "wisdom", "cha": "charisma",
}


def _attack(source: CatalogAttack2014) -> WeaponAttack:
    try:
        kind = WeaponAttackKind.MELEE if source.kind == "melee" else WeaponAttackKind.RANGED
        weapon = Weapon(
            id=source.id, name=source.name, attack_kind=kind,
            dice_count=source.damage.dice_count, dice_size=source.damage.dice_size,
            damage_type=source.damage.type, animation="projectile" if source.kind == "ranged" else "melee",
            reach_ft=source.reach_ft, normal_range_ft=source.normal_range_ft,
            long_range_ft=source.long_range_ft,
        )
        return WeaponAttack(
            id=source.id, weapon=weapon, attack_bonus=source.attack_bonus,
            damage_bonus=source.damage.bonus,
            fixed_damage=source.damage.average if source.damage.dice_count == 0 else None,
        )
    except Exception as exc:
        logger.exception("Failed to compile 2014 catalog attack %s.", source.id)
        raise RuntimeError(f"2014 attack {source.id} could not be compiled.") from exc


def _ability_scores(source: CatalogMonster2014) -> AbilityScores:
    try:
        return AbilityScores(**{name: source.abilities[key] for key, name in _ABILITY_NAMES.items()})
    except Exception as exc:
        logger.exception("Invalid 2014 ability scores for %s.", source.id)
        raise RuntimeError(f"2014 monster {source.id} has invalid ability scores.") from exc


def unsupported_mechanics_2014(source: CatalogMonster2014) -> list[str]:
    try:
        attack_names = {attack.name for attack in source.attacks}
        blockers = [f"defense:{text}" for text in source.unsupported_defense_text]
        blockers.extend(f"action:{name}" for name in source.action_names if name not in attack_names)
        blockers.extend(f"trait:{name}" for name in source.trait_names)
        blockers.extend(f"reaction:{name}" for name in source.reaction_names)
        blockers.extend(f"legendary:{name}" for name in source.legendary_action_names)
        if not source.attacks:
            blockers.append("attack:no-structured-attack")
        return blockers
    except Exception as exc:
        logger.exception("Failed to inventory 2014 mechanics for %s.", source.id)
        raise RuntimeError(f"2014 monster {source.id} mechanics could not be inventoried.") from exc


def compile_monster_2014(source: CatalogMonster2014) -> CombatantTemplate:
    try:
        blockers = unsupported_mechanics_2014(source)
        if blockers:
            raise ValueError(f"unsupported 2014 mechanics: {', '.join(blockers)}")
        attacks = [_attack(item) for item in source.attacks]
        movement = MovementModes(
            walk_ft=source.speed.get("walk", 0), fly_ft=source.speed.get("fly", 0),
            climb_ft=source.speed.get("climb", 0), swim_ft=source.speed.get("swim", 0),
            burrow_ft=source.speed.get("burrow", 0),
        )
        saves = {_ABILITY_NAMES.get(key, key): value for key, value in source.saving_throws.items()}
        dex = source.abilities["dex"]
        return CombatantTemplate(
            id=f"2014-{source.id}", name=source.name, archetype=source.name,
            challenge_rating=source.challenge_rating, kind="monster",
            creature_type=source.creature_type, size=source.size,
            ability_scores=_ability_scores(source), armor_class=source.armor_class,
            max_hp=source.max_hp, speed_ft=movement.walk_ft, movement_modes=movement,
            initiative_bonus=(dex - 10) // 2, weapon_attack=attacks[0],
            alternate_weapon_attacks=attacks[1:], saving_throw_bonuses=saves,
            skill_bonuses=source.skills, damage_resistances=source.damage_resistances,
            damage_immunities=source.damage_immunities,
            damage_vulnerabilities=source.damage_vulnerabilities,
            condition_immunities=source.condition_immunities,
            visual=VisualLoadout(armor="source", main_hand=attacks[0].weapon.id, body_style=source.creature_type),
            source=f"2014 JSON catalog: {source.id}",
        )
    except Exception as exc:
        logger.exception("Failed to compile 2014 monster %s.", source.id)
        raise RuntimeError(f"2014 monster {source.id} could not be compiled: {exc}") from exc


def load_catalog_2014(path: Path = CATALOG_ROOT) -> list[CatalogMonster2014]:
    try:
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            files = sorted(path.glob("catalog_*.json")) or [path / "mvp_catalog.json"]
            payload = []
            for file in files:
                payload.extend(json.loads(file.read_text(encoding="utf-8")))
        return _MONSTERS.validate_python(payload)
    except Exception as exc:
        logger.exception("Failed to load 2014 monster catalog from %s.", path)
        raise RuntimeError(f"2014 monster catalog could not be loaded from {path}.") from exc


def monster_by_id_2014(monster_id: str, path: Path = CATALOG_ROOT) -> CombatantTemplate:
    try:
        source = next(item for item in load_catalog_2014(path) if item.id == monster_id)
        return compile_monster_2014(source)
    except StopIteration as exc:
        raise KeyError(f"Unknown 2014 monster id: {monster_id}") from exc
