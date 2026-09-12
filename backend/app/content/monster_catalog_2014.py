from __future__ import annotations

import json
import logging
from pathlib import Path

from pydantic import TypeAdapter

from app.content.monster_catalog_2014_compile_support import (
    ability_scores_2014,
    resources_2014,
    saving_throw_bonuses_2014,
)
from app.content.monster_catalog_2014_defenses import conditional_resistances_2014, unresolved_defenses_2014
from app.content.monster_catalog_2014_models import CatalogAttack2014, CatalogMonster2014
from app.content.monster_catalog_2014_traits import combat_traits_2014, unresolved_traits_2014
from app.domain.models import (
    AttackActionDefinition, AttackActionSlot, CombatantTemplate, OnHitDamage,
    VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind,
)
from app.domain.movement import MovementModes
from app.domain.reactions import ParryReaction
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
CATALOG_ROOT = Path(__file__).resolve().parents[3] / "data" / "monsters" / "2014"
MVP_CATALOG_PATH = CATALOG_ROOT / "mvp_catalog.json"
_MONSTERS = TypeAdapter(list[CatalogMonster2014])


def _attack(source: CatalogAttack2014, *, magical: bool = False) -> WeaponAttack:
    try:
        kind = WeaponAttackKind.MELEE if source.kind == "melee" else WeaponAttackKind.RANGED
        weapon = Weapon(
            id=source.id, name=source.name, attack_kind=kind,
            dice_count=source.damage.dice_count, dice_size=source.damage.dice_size,
            damage_type=source.damage.type, animation="projectile" if source.kind == "ranged" else "melee",
            reach_ft=source.reach_ft, normal_range_ft=source.normal_range_ft,
            long_range_ft=source.long_range_ft, magical=magical,
        )
        riders = [
            OnHitDamage(source=f"{source.name} secondary damage", dice_count=item.dice_count,
                        dice_size=item.dice_size, damage_bonus=item.bonus, damage_type=item.type)
            for item in source.on_hit_damage
        ]
        return WeaponAttack(
            id=source.id, weapon=weapon, attack_bonus=source.attack_bonus,
            damage_bonus=source.damage.bonus,
            fixed_damage=source.damage.average if source.damage.dice_count == 0 else None,
            on_hit_damage=riders, on_hit_save_effect=source.on_hit_save_effect,
            charge_profile=source.charge_profile,
        )
    except Exception as exc:
        logger.exception("Failed to compile 2014 catalog attack %s.", source.id)
        raise RuntimeError(f"2014 attack {source.id} could not be compiled.") from exc


def _multiattack(source: CatalogMonster2014, attacks: list[WeaponAttack]) -> AttackActionDefinition | None:
    if not source.multiattack_slots: return None
    known = {attack.id for attack in attacks}; slots: list[AttackActionSlot] = []
    for choices in source.multiattack_slots:
        if not choices or any(attack_id not in known for attack_id in choices):
            raise ValueError(f"Invalid Multiattack attack ids for {source.id}: {choices}")
        slots.append(AttackActionSlot(attack_ids=choices))
    return AttackActionDefinition(id=f"2014-{source.id}-multiattack", name="Multiattack", slots=slots)


def unsupported_mechanics_2014(source: CatalogMonster2014) -> list[str]:
    try:
        attack_names = {attack.name for attack in source.attacks}; supported_actions = set(attack_names)
        if source.multiattack_slots: supported_actions.add("Multiattack")
        supported_reactions = {"Parry"} if source.parry_ac_bonus is not None else set()
        blockers = [f"defense:{text}" for text in unresolved_defenses_2014(source.unsupported_defense_text)]
        blockers.extend(f"attack-detail:{attack.name}" for attack in source.attacks if not attack.source_complete)
        blockers.extend(f"action:{name}" for name in source.action_names if name not in supported_actions)
        blockers.extend(f"trait:{name}" for name in unresolved_traits_2014(source.trait_names))
        if "Charge" in source.trait_names and not any(attack.charge_profile for attack in source.attacks): blockers.append("trait:Charge")
        blockers.extend(f"reaction:{name}" for name in source.reaction_names if name not in supported_reactions)
        blockers.extend(f"legendary:{name}" for name in source.legendary_action_names)
        if not source.attacks: blockers.append("attack:no-structured-attack")
        return blockers
    except Exception as exc:
        logger.exception("Failed to inventory 2014 mechanics for %s.", source.id)
        raise RuntimeError(f"2014 monster {source.id} mechanics could not be inventoried.") from exc


def compile_monster_2014(source: CatalogMonster2014) -> CombatantTemplate:
    try:
        blockers = unsupported_mechanics_2014(source)
        if blockers: raise ValueError(f"unsupported 2014 mechanics: {', '.join(blockers)}")
        traits = combat_traits_2014(source.trait_names); magical = CombatTrait.MAGIC_WEAPONS in traits
        attacks = [_attack(item, magical=magical) for item in source.attacks]
        movement = MovementModes(
            walk_ft=source.speed.get("walk", 0), fly_ft=source.speed.get("fly", 0),
            climb_ft=source.speed.get("climb", 0), swim_ft=source.speed.get("swim", 0), burrow_ft=source.speed.get("burrow", 0),
        )
        dex = source.abilities["dex"]
        return CombatantTemplate(
            id=f"2014-{source.id}", name=source.name, archetype=source.name,
            challenge_rating=source.challenge_rating, kind="monster", creature_type=source.creature_type, size=source.size,
            ability_scores=ability_scores_2014(source), armor_class=source.armor_class, max_hp=source.max_hp,
            speed_ft=movement.walk_ft, movement_modes=movement, initiative_bonus=(dex - 10) // 2,
            weapon_attack=attacks[0], alternate_weapon_attacks=attacks[1:], attack_action=_multiattack(source, attacks),
            saving_throw_bonuses=saving_throw_bonuses_2014(source), skill_bonuses=source.skills, damage_resistances=source.damage_resistances,
            conditional_damage_resistances=conditional_resistances_2014(source.unsupported_defense_text),
            damage_immunities=source.damage_immunities, damage_vulnerabilities=source.damage_vulnerabilities,
            condition_immunities=source.condition_immunities, combat_traits=traits, resources=resources_2014(source),
            parry_reaction=ParryReaction(ac_bonus=source.parry_ac_bonus) if source.parry_ac_bonus is not None else None,
            visual=VisualLoadout(armor="source", main_hand=attacks[0].weapon.id, body_style=source.creature_type),
            source=f"2014 JSON catalog: {source.id}",
        )
    except Exception as exc:
        logger.exception("Failed to compile 2014 monster %s.", source.id)
        raise RuntimeError(f"2014 monster {source.id} could not be compiled: {exc}") from exc


def load_catalog_2014(path: Path = CATALOG_ROOT) -> list[CatalogMonster2014]:
    try:
        if path.is_file(): payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            canonical = path / "catalog.json"; files = [canonical] if canonical.exists() else sorted(path.glob("catalog_*.json"))
            files = files or [path / "mvp_catalog.json"]; payload = []
            for file in files: payload.extend(json.loads(file.read_text(encoding="utf-8")))
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
