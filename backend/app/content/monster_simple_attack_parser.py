from __future__ import annotations

import re

from app.content.monster_attack_roll_modifier_source_audit import parse_attack_roll_modifier
from app.content.monster_bloodied_source_damage import extract_bloodied_replacement
from app.content.monster_limited_use_source_audit import parse_action_recharges
from app.content.monster_simple_control_rider import parse_simple_control_rider
from app.content.monster_simple_hit_modifier_rider import parse_simple_hit_modifier_riders
from app.domain.models import DamageType, OnHitDamage, Weapon, WeaponAttack, WeaponAttackKind

_DAMAGE_TYPES = r"Acid|Bludgeoning|Cold|Fire|Force|Lightning|Necrotic|Piercing|Poison|Psychic|Radiant|Slashing|Thunder"
_SAVE_ABILITY = r"Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma"
_NEXT_ACTION = (
    r"(?:\s+[A-Z][A-Za-z0-9 ’'()/-]+\.\s+(?:"
    r"(?:Melee|Ranged|Melee or Ranged)\s+Attack Roll:|"
    rf"(?:{_SAVE_ABILITY})\s+Saving Throw:))|$"
)
_ATTACK = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9 ’'()/-]+)\.\s+(?P<mode>Melee|Ranged|Melee or Ranged)\s+Attack Roll:\s*"
    r"(?P<bonus>[+-]?\d+)\s*(?P<conditional>\([^)]*\))?,\s*(?P<range>.*?)\.\s+Hit:\s*(?P<hit>.*?)"
    rf"(?={_NEXT_ACTION})",
    re.S,
)
_DICE_DAMAGE = re.compile(
    rf"\d+\s*\(\s*(?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\s*\)\s+(?P<type>{_DAMAGE_TYPES})\s+damage",
    re.I,
)
_FIXED_DAMAGE = re.compile(rf"^(?P<amount>\d+)\s+(?P<type>{_DAMAGE_TYPES})\s+damage\b", re.I)
_FIXED_EXTRA = re.compile(rf"\bplus\s+(?P<amount>\d+)\s+(?P<type>{_DAMAGE_TYPES})\s+damage\b", re.I)
_REACH = re.compile(r"reach\s+(\d+)\s*ft", re.I)
_RANGE = re.compile(r"range\s+(\d+)(?:\s*/\s*(\d+))?\s*ft", re.I)
_RECHARGE_SUFFIX = re.compile(r"\s*\(\s*Recharge\s+\d(?:\s*[-–]\s*\d)?\s*\)\s*$", re.I)


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def first_attack_start(actions: str) -> int:
    match = _ATTACK.search(actions)
    if match is None:
        raise ValueError("no simple attack roll found")
    return match.start()


def _damage(hit: str) -> tuple[int, int, int, DamageType, int | None, list[OnHitDamage]]:
    matches = list(_DICE_DAMAGE.finditer(hit))
    if matches:
        first = matches[0]
        bonus = int(first.group("bonus") or 0) * (-1 if first.group("sign") == "-" else 1)
        extras: list[OnHitDamage] = []
        for item in matches[1:]:
            extra_bonus = int(item.group("bonus") or 0) * (-1 if item.group("sign") == "-" else 1)
            extras.append(OnHitDamage(
                source=item.group("type").title(), dice_count=int(item.group("count")), dice_size=int(item.group("size")),
                damage_bonus=extra_bonus, damage_type=DamageType(item.group("type").lower()),
            ))
        for item in _FIXED_EXTRA.finditer(hit):
            extras.append(OnHitDamage(
                source=item.group("type").title(), dice_count=0, dice_size=2,
                damage_bonus=int(item.group("amount")), damage_type=DamageType(item.group("type").lower()),
            ))
        return int(first.group("count")), int(first.group("size")), bonus, DamageType(first.group("type").lower()), None, extras
    fixed = _FIXED_DAMAGE.search(hit.strip())
    if fixed:
        return 0, 2, 0, DamageType(fixed.group("type").lower()), int(fixed.group("amount")), []
    raise ValueError("attack damage is not a simple supported damage clause")


def parse_simple_attacks(row: dict[str, object]) -> list[WeaponAttack]:
    attacks: list[WeaponAttack] = []
    try:
        recharges = parse_action_recharges(row)
        monster_slug = _slug(str(row["name"]))
        for match in _ATTACK.finditer(str(row["actions"])):
            printed_name = match.group("name").strip()
            attack_name = _RECHARGE_SUFFIX.sub("", printed_name).strip()
            clean_hit, bloodied = extract_bloodied_replacement(match.group("hit"))
            clean_hit, control, prone_size = parse_simple_control_rider(clean_hit)
            clean_hit, hit_modifiers = parse_simple_hit_modifier_riders(clean_hit)
            count, size, damage_bonus, damage_type, fixed, extras = _damage(clean_hit)
            modes = ["melee", "ranged"] if match.group("mode").lower() == "melee or ranged" else [match.group("mode").lower()]
            conditional = parse_attack_roll_modifier(match.group("conditional")) if match.group("conditional") else None
            resource_id = f"srd-{monster_slug}-{_slug(attack_name)}-recharge" if attack_name in recharges else None
            for mode in modes:
                reach = _REACH.search(match.group("range")); ranged = _RANGE.search(match.group("range"))
                if mode == "melee" and reach is None:
                    raise ValueError("simple melee attack lacks reach")
                if mode == "ranged" and ranged is None:
                    raise ValueError("simple ranged attack lacks range")
                suffix = f"-{mode}" if len(modes) > 1 else ""
                attack_id = f"srd-{monster_slug}-{_slug(attack_name)}{suffix}"
                normal_range = int(ranged.group(1)) if ranged else None
                long_range = int(ranged.group(2) or ranged.group(1)) if ranged else None
                weapon = Weapon(
                    id=f"{attack_id}-weapon", name=attack_name, attack_kind=WeaponAttackKind(mode),
                    dice_count=count, dice_size=size, damage_type=damage_type, reach_ft=int(reach.group(1)) if reach else 5,
                    normal_range_ft=normal_range, long_range_ft=long_range,
                    animation="strike",
                )
                attacks.append(WeaponAttack(
                    id=attack_id, weapon=weapon, attack_bonus=int(match.group("bonus")), damage_bonus=damage_bonus,
                    fixed_damage=fixed, on_hit_damage=extras, on_hit_modifier_effects=hit_modifiers,
                    control_effect=control, knocks_prone_max_size=prone_size,
                    conditional_attack_modifiers=[conditional] if conditional is not None else [],
                    conditional_damage=[bloodied] if bloodied is not None else [], resource_id=resource_id,
                ))
        if not attacks:
            raise ValueError("no simple attacks parsed")
        return attacks
    except Exception as exc:
        raise ValueError(f"simple attack parsing failed for {row.get('name', '<unknown>')}") from exc
