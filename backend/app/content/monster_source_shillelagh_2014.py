"""2014 Shillelagh: existing timed buff + effect-bound weapon damage.

No spell-specific runtime resolver. Source cards retain the printed enhanced
alternate; combat selects the normal weapon, whose replacement damage only
activates after this generic timed buff has actually been cast.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_STAFF = re.compile(
    r"Melee Weapon Attack: \+(?P<base>\d+) to hit "
    r"\(\+(?P<enchanted>\d+) to hit with shillelagh\), "
    r"reach (?P<reach>\d+) ft\., one target\. "
    r"Hit: (?P<normal_avg>\d+) \((?P<normal_dice>\d+)d(?P<normal_size>\d+)\) "
    r"bludgeoning damage, (?P<two_avg>\d+) "
    r"\((?P<two_dice>\d+)d(?P<two_size>\d+)\) "
    r"bludgeoning damage if wielded with two hands, "
    r"or (?P<enchant_avg>\d+) \((?P<enchant_dice>\d+)d"
    r"(?P<enchant_size>\d+) \+ (?P<enchant_bonus>\d+)\) "
    r"bludgeoning damage with shillelagh\.",
    re.IGNORECASE,
)


def _source(monster: SourceMonster2014):
    """Confirm every printed attack option and immutable cantrip identity."""
    source = monster.spellcasting
    if not isinstance(source, dict) or source.get("source_complete") is not True:
        return None
    entries = source.get("spells")
    if not isinstance(entries, list) or not any(
        isinstance(v, dict) and v.get("id") == "shillelagh" for v in entries
    ):
        return None
    if not any(v == {"id": "shillelagh", "name": "shillelagh", "level": 0}
               for v in entries):
        raise ValueError("Shillelagh's printed spell entry changed.")
    actions = {attack.id: attack for attack in monster.attacks}
    ids = ("quarterstaff", "quarterstaff-two-handed", "quarterstaff-shillelagh")
    if not all(key in actions for key in ids) or len(actions) != 3:
        raise ValueError("Shillelagh's printed staff variants are incomplete.")
    normal, two, enchanted = (actions[key] for key in ids)
    text = source_sections_2014(monster.source_actions).get("Quarterstaff", "")
    match = _STAFF.fullmatch(text)
    if match is None:
        raise ValueError("Shillelagh's complete Quarterstaff source changed.")
    fields = {key: int(value) for key, value in match.groupdict().items()}
    normal_damage, two_damage, enchanted_damage = (
        normal.damage, two.damage, enchanted.damage,
    )
    if (
        fields["base"] != normal.attack_bonus
        or fields["enchanted"] != enchanted.attack_bonus
        or fields["reach"] != normal.reach_ft
        or not all(item.kind == "melee" and item.name == "Quarterstaff"
                   and item.source_complete and not item.on_hit_damage
                   and not item.conditional_damage
                   for item in (normal, two, enchanted))
        or not all(item.damage.type == "bludgeoning"
                   for item in (normal, two, enchanted))
        or (fields["normal_avg"], fields["normal_dice"], fields["normal_size"])
           != (normal_damage.average, normal_damage.dice_count, normal_damage.dice_size)
        or (fields["two_avg"], fields["two_dice"], fields["two_size"])
           != (two_damage.average, two_damage.dice_count, two_damage.dice_size)
        or (fields["enchant_avg"], fields["enchant_dice"], fields["enchant_size"],
            fields["enchant_bonus"]) != (
            enchanted_damage.average, enchanted_damage.dice_count,
            enchanted_damage.dice_size, enchanted_damage.bonus,
        )
        or enchanted.attack_bonus <= normal.attack_bonus
        or source.get("ability") != "wisdom"
    ):
        raise ValueError("Shillelagh's parsed weapon statistics no longer match.")
    return normal, two, enchanted


def source_shillelagh_buff_2014(monster: SourceMonster2014) -> TimedSelfBuffAction | None:
    """A Bonus Action prepares the enhanced printed staff for one minute."""
    try:
        proof = _source(monster)
        if proof is None:
            return None
        normal, two, enchanted = proof
        bonus = enchanted.attack_bonus - normal.attack_bonus
        return TimedSelfBuffAction(
            id="shillelagh", name="Shillelagh", action_cost="bonus_action",
            duration_rounds=10, expiry_timing="source_turn_start",
            magical_effect=True, priority=60,
            modifier_effects=[
                SpellModifierEffect(
                    kind="attack-roll-flat", flat_bonus=bonus,
                    weapon_id=attack_id_2014(monster, attack.id),
                )
                for attack in (normal, two)
            ] + [
                SpellModifierEffect(
                    kind="damage-source-qualifier",
                    weapon_id=attack_id_2014(monster, attack.id),
                    source_qualifier="magical",
                )
                for attack in (normal, two)
            ],
            animation="buff",
        )
    except Exception:
        logger.exception("2014 Shillelagh source/buff proof failed for %s.", monster.id)
        raise


def source_shillelagh_attacks_2014(monster: SourceMonster2014) -> list[SourceAttack2014]:
    """Discard powered runtime alternative; put its source dice behind buff state."""
    try:
        proof = _source(monster)
        if proof is None:
            return list(monster.attacks)
        normal, two, enchanted = proof
        augmented = []
        for attack in monster.attacks:
            if attack.id == enchanted.id:
                continue
            if attack.id not in (normal.id, two.id):
                augmented.append(attack)
                continue
            augmented.append(attack.model_copy(update={"conditional_damage": [{
                "trigger": "attacker_active_effect", "required_effect_id": "shillelagh",
                "mode": "replace_weapon",
                "dice_count": enchanted.damage.dice_count,
                "dice_size": enchanted.damage.dice_size,
                "damage_bonus": enchanted.damage.bonus,
                "damage_type": enchanted.damage.type,
            }]}))
        return augmented
    except Exception:
        logger.exception("2014 source Shillelagh weapon conditioning failed for %s.", monster.id)
        raise
