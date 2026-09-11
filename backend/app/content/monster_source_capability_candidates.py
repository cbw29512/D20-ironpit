from __future__ import annotations

import re

from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.monster_source_attack_riders import parse_attack_riders
from app.content.monster_source_save_candidates import source_save_candidates
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed
from app.content.unarmed_opportunity_profiles import monster_unarmed_profile
from app.domain.capabilities import CombatantDefinition
from app.domain.capability_attacks import AttackCapabilityDefinition, CapabilityActionSlot, MultiattackCapabilityDefinition
from app.domain.capability_effects import DamageEffectDefinition, DiceSpec
from app.domain.combatants import VisualLoadout
from app.domain.size import CreatureSize
from app.domain.weapons import DamageType, WeaponAttackKind

_ATTACK = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+(?P<kind>Melee|Ranged|Melee or Ranged) Attack Roll:\s*"
    r"(?P<bonus>[+-]?\d+),\s*(?P<range>reach\s+\d+\s*ft\.|range\s+\d+(?:/\d+)?\s*ft\."
    r"|reach\s+\d+\s*ft\.\s+or\s+range\s+\d+(?:/\d+)?\s*ft\.)\s*Hit:\s*"
    r"(?P<average>\d+)\s*\((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<mod>\d+))?\)\s*"
    r"(?P<dtype>[A-Za-z]+) damage(?P<extra>\s+plus\s+\d+\s*\(\d+d\d+(?:\s*[+-]\s*\d+)?\)\s+[A-Za-z]+\s+damage)?"
    r"(?P<tail>[^.]*)\.", re.I,
)
_EXTRA = re.compile(r"plus\s+\d+\s*\((\d+)d(\d+)(?:\s*([+-])\s*(\d+))?\)\s+([A-Za-z]+)\s+damage", re.I)
_ON_HIT_SAVE_BLOCK = re.compile(
    r"(?:(?:If|The target)[^.]*following effect\.\s*)?"
    r"(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw:\s*DC\s*\d+[^.]*\.\s*"
    r"Failure:\s*[^.]+\.", re.I,
)
_MULTI_COUNT = re.compile(r"Multiattack\.\s+The\s+[^.]+?\s+makes\s+(one|two|three|four|five|six)\s+([A-Za-z’' -]+?)\s+attacks?\.", re.I)
_MULTI_GENERIC = re.compile(r"Multiattack\.\s+The\s+[^.]+?\s+makes\s+(one|two|three|four|five|six)\s+attacks?,\s+using\s+([^.]+?)\s+in any combination\.", re.I)
_WORD_COUNT = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _bonus(match: re.Match[str]) -> int:
    value = int(match.group("mod") or 0)
    return -value if match.group("sign") == "-" else value


def _ranges(text: str) -> tuple[int, int | None, int | None]:
    reach = re.search(r"reach\s+(\d+)", text, re.I)
    ranged = re.search(r"range\s+(\d+)(?:/(\d+))?", text, re.I)
    normal = int(ranged.group(1)) if ranged else None
    long = int(ranged.group(2) or ranged.group(1)) if ranged else None
    return int(reach.group(1)) if reach else 5, normal, long


def _rider_text(actions: str, match: re.Match[str]) -> str:
    text = match.group("tail") or ""
    following = actions[match.end():].lstrip()
    save_block = _ON_HIT_SAVE_BLOCK.match(following)
    if save_block:
        return text + ". " + save_block.group(0)
    if re.match(r"(?:If|Until|The target|Whenever|While)\b", following, re.I):
        text += ". " + following.split(".", 1)[0]
    return text


def _attack(row: dict[str, object], actions: str, match: re.Match[str]) -> AttackCapabilityDefinition:
    name = match.group("name").strip()
    kind = WeaponAttackKind(match.group("kind").lower().replace(" ", "_"))
    reach, normal, long = _ranges(match.group("range"))
    effects = parse_attack_riders(_rider_text(actions, match))
    extra = _EXTRA.search(match.group("extra") or "")
    if extra:
        mod = int(extra.group(4) or 0) * (-1 if extra.group(3) == "-" else 1)
        effects.insert(0, DamageEffectDefinition(
            source="Source extra damage", dice=DiceSpec(count=int(extra.group(1)), size=int(extra.group(2)), bonus=mod),
            damage_type=DamageType(extra.group(5).lower()),
        ))
    attack_id = f"srd-{_slug(str(row['name']))}-{_slug(name)}"
    return AttackCapabilityDefinition(
        id=attack_id, name=name, weapon_id=f"{attack_id}-weapon", attack_kind=kind,
        attack_bonus=int(match.group("bonus")),
        damage=DiceSpec(count=int(match.group("count")), size=int(match.group("size")), bonus=_bonus(match)),
        damage_type=DamageType(match.group("dtype").lower()), animation="strike", reach_ft=reach,
        normal_range_ft=normal, long_range_ft=long, effects=effects,
    )


def _multiattack(row: dict[str, object], attacks: list[AttackCapabilityDefinition]) -> MultiattackCapabilityDefinition | None:
    text = str(row.get("actions", ""))
    match = _MULTI_COUNT.search(text)
    if match:
        wanted = match.group(2).strip().lower().rstrip("s")
        ids = [item.id for item in attacks if item.name.lower().rstrip("s") == wanted]
        if ids:
            return MultiattackCapabilityDefinition(id=f"srd-{_slug(str(row['name']))}-multiattack", slots=[CapabilityActionSlot(attack_ids=ids) for _ in range(_WORD_COUNT[match.group(1).lower()])])
    match = _MULTI_GENERIC.search(text)
    if match:
        ids = [item.id for item in attacks if re.search(rf"\b{re.escape(item.name)}\b", match.group(2), re.I)]
        if ids:
            return MultiattackCapabilityDefinition(id=f"srd-{_slug(str(row['name']))}-multiattack", slots=[CapabilityActionSlot(attack_ids=ids) for _ in range(_WORD_COUNT[match.group(1).lower()])])
    return None


def source_candidate_definitions(excluded_ids: set[str]) -> dict[str, CombatantDefinition]:
    candidates: dict[str, CombatantDefinition] = {}
    for row in load_monster_rows():
        definition_id = f"srd-{_slug(str(row['name']))}"
        if definition_id in excluded_ids:
            continue
        try:
            action_text = str(row.get("actions", ""))
            attacks = [_attack(row, action_text, match) for match in _ATTACK.finditer(action_text)]
            if not attacks:
                continue
            save_actions, resources = source_save_candidates(row)
            defenses = parse_defense_profile(row)
            initiative = re.search(r"\bInitiative\s+([+-]?\d+)", str(row.get("rawText", "")), re.I)
            if initiative is None:
                continue
            candidates[definition_id] = CombatantDefinition(
                id=definition_id, name=str(row["name"]), archetype="source-derived candidate", kind="monster",
                challenge_rating=str(row["challenge"]).split()[0], size=CreatureSize(str(row["size"]).split()[0].lower()),
                armor_class=int(re.search(r"\d+", str(row["armorClass"])).group()), max_hp=int(re.search(r"\d+", str(row["hitPoints"])).group()),
                speed_ft=standard_arena_closing_speed(row["speed"]), movement_modes=parse_movement_profile(row["speed"]),
                initiative_bonus=int(initiative.group(1)), attacks=attacks, primary_attack_id=attacks[0].id,
                attack_action=_multiattack(row, attacks), save_actions=save_actions, resources=resources,
                unarmed_opportunity_attack=monster_unarmed_profile(row),
                damage_vulnerabilities=sorted(defenses["damage_vulnerabilities"]), damage_resistances=sorted(defenses["damage_resistances"]),
                damage_immunities=sorted(defenses["damage_immunities"]), condition_immunities=sorted(defenses["condition_immunities"]),
                visual=VisualLoadout(armor="natural", main_hand=attacks[0].name, body_style="monster"), source=str(row["sourceReference"]),
            )
        except (AttributeError, TypeError, ValueError):
            continue
    return candidates
