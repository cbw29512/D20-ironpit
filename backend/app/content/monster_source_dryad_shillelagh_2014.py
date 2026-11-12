"""Source-prove a 2014 innate Club enchantment; generic buffs own combat.

All numeric combat outcomes are read from exact printed source declarations.
No monster ID or action label changes universal attack/damage resolution.
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

_CLUB = re.compile(
    r"Melee Weapon Attack: \+(?P<base>\d+) to hit "
    r"\(\+(?P<enchanted>\d+) to hit with shillelagh\), "
    r"reach (?P<reach>\d+) ft\., one target\. "
    r"Hit: (?P<normal_avg>\d+) \((?P<normal_d>\d+)d(?P<normal_s>\d+)\) "
    r"bludgeoning damage, or (?P<ench_avg>\d+) "
    r"\((?P<ench_d>\d+)d(?P<ench_s>\d+) \+ (?P<ench_bonus>\d+)\) "
    r"bludgeoning damage with shillelagh\.",
    re.IGNORECASE,
)


def _source(monster: SourceMonster2014) -> tuple[SourceAttack2014, SourceAttack2014] | None:
    """Reject every altered printed Club/spell source instead of guessing."""
    try:
        attacks = {attack.id: attack for attack in monster.attacks}
        if "club-shillelagh" not in attacks:
            return None
        if set(attacks) != {"club", "club-shillelagh"}:
            raise ValueError("Innate enchanted Club variants changed.")
        source = monster.innate_spellcasting
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            raise ValueError("Innate Shillelagh requires complete printed spell source.")
        spells = source.get("spells")
        if not isinstance(spells, list):
            raise ValueError("Innate Shillelagh requires a structured spell list.")
        spell = {
            "id": "shillelagh", "name": "shillelagh", "usage": "per_day",
            "uses_per_day": 1, "shared_pool": False, "qualifier": None,
        }
        if spells.count(spell) != 1 or source.get("ability") != "charisma":
            raise ValueError("Innate Shillelagh identity/frequency/ability changed.")
        traits = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Innate Spellcasting", "").casefold()
        if "1/day each: barkskin, pass without trace, shillelagh" not in traits:
            raise ValueError("Printed innate Shillelagh frequency changed.")
        printed = source_sections_2014(monster.source_actions).get("Club", "")
        match = _CLUB.fullmatch(printed)
        if match is None:
            raise ValueError("Complete printed Shillelagh Club paragraph changed.")
        values = {key: int(value) for key, value in match.groupdict().items()}
        normal, enchanted = attacks["club"], attacks["club-shillelagh"]
        if (
            not all(a.name == "Club" and a.kind == "melee"
                    and a.source_complete and not a.conditional_damage
                    and not a.on_hit_damage for a in (normal, enchanted))
            or values["base"] != normal.attack_bonus
            or values["enchanted"] != enchanted.attack_bonus
            or values["enchanted"] <= values["base"]
            or values["reach"] != normal.reach_ft
            or normal.reach_ft != enchanted.reach_ft
            or normal.damage.type != "bludgeoning"
            or enchanted.damage.type != "bludgeoning"
            or (values["normal_avg"], values["normal_d"], values["normal_s"])
               != (normal.damage.average, normal.damage.dice_count, normal.damage.dice_size)
            or (values["ench_avg"], values["ench_d"], values["ench_s"], values["ench_bonus"])
               != (enchanted.damage.average, enchanted.damage.dice_count,
                   enchanted.damage.dice_size, enchanted.damage.bonus)
        ):
            raise ValueError("Printed Shillelagh Club statistics differ from source attacks.")
        return normal, enchanted
    except Exception:
        logger.exception("Innate 2014 Club Shillelagh source verification failed.")
        raise


def innate_club_shillelagh_buff_2014(monster: SourceMonster2014) -> TimedSelfBuffAction | None:
    """Source-owned 1/day cost, generic 10-round weapon-enchantment buff."""
    try:
        proven = _source(monster)
        if proven is None:
            return None
        normal, enchanted = proven
        weapon_id = attack_id_2014(monster, normal.id)
        return TimedSelfBuffAction(
            id="shillelagh", name="Shillelagh", action_cost="bonus_action",
            resource_id="shillelagh", resource_cost=1,
            duration_rounds=10, expiry_timing="source_turn_start",
            magical_effect=True, priority=60,
            modifier_effects=[
                SpellModifierEffect(
                    kind="attack-roll-flat",
                    flat_bonus=enchanted.attack_bonus - normal.attack_bonus,
                    weapon_id=weapon_id,
                ),
                SpellModifierEffect(
                    kind="damage-source-qualifier", weapon_id=weapon_id,
                    source_qualifier="magical",
                ),
            ],
            animation="buff",
        )
    except Exception:
        logger.exception("Innate 2014 Club Shillelagh buff binding failed.")
        raise


def source_innate_club_shillelagh_attacks_2014(
    monster: SourceMonster2014, attacks: list[SourceAttack2014],
) -> list[SourceAttack2014]:
    """Leave printed source immutable and remove always-on runtime enchantment."""
    try:
        proven = _source(monster)
        if proven is None:
            return attacks
        normal, enchanted = proven
        result = []
        for attack in attacks:
            if attack.id == enchanted.id:
                continue
            if attack.id != normal.id:
                result.append(attack)
                continue
            result.append(attack.model_copy(update={"conditional_damage": [{
                "trigger": "attacker_active_effect", "required_effect_id": "shillelagh",
                "mode": "replace_weapon", "dice_count": enchanted.damage.dice_count,
                "dice_size": enchanted.damage.dice_size,
                "damage_bonus": enchanted.damage.bonus,
                "damage_type": enchanted.damage.type,
            }]}))
        return result
    except Exception:
        logger.exception("Innate 2014 Club Shillelagh attack conditioning failed.")
        raise
