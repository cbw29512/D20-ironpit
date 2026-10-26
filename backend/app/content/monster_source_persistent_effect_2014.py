"""Strict source proof for persistent failed-save attack effects."""
from __future__ import annotations

import logging
import re
from pydantic import BaseModel, Field

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


class PersistentSaveEffectProof2014(BaseModel):
    """Immutable source parameters; live curse state belongs to the fight."""

    save_ability: str = Field(min_length=1)
    dc: int = Field(ge=1, le=40)
    effect_id: str = Field(min_length=1)
    curse_id: str = Field(min_length=1)
    cannot_regain_hit_points: bool
    allowed_removal_action_ids: list[str]
    delayed_max_hp_reduction_delay_hours: int = Field(ge=1)
    delayed_max_hp_reduction_dice_count: int = Field(ge=1, le=40)
    delayed_max_hp_reduction_dice_size: int = Field(ge=2, le=100)
    delayed_max_hp_reduction_zero_kills: bool


_SEMANTIC = re.compile(
    r"saving throw or be cursed with .+?\. The cursed target can't regain hit points, "
    r"and its hit point maximum decreases by \d+ \(\d+d\d+\) for every \d+ hours "
    r"that elapse\..+?The curse lasts until removed by .+?\.",
    re.IGNORECASE,
)
_PATTERN = re.compile(
    r"Melee Weapon Attack: \+(?P<hit>\d+) to hit, reach (?P<reach>\d+) ft\., "
    r"one target\. Hit: (?P<base_avg>\d+) \((?P<base_n>\d+)d(?P<base_s>\d+) "
    r"\+ (?P<base_bonus>\d+)\) (?P<base_type>\w+) damage plus "
    r"(?P<extra_avg>\d+) \((?P<extra_n>\d+)d(?P<extra_s>\d+)\) "
    r"(?P<extra_type>\w+) damage\. If the target is a creature, it must succeed "
    r"on a DC (?P<dc>\d+) (?P<ability>Constitution) saving throw or be cursed "
    r"with (?P<curse>[\w ]+)\. The cursed target can't regain hit points, and its "
    r"hit point maximum decreases by (?P<loss_avg>\d+) \((?P<loss_n>\d+)d"
    r"(?P<loss_s>\d+)\) for every (?P<hours>\d+) hours that elapse\. If the curse "
    r"reduces the target's hit point maximum to 0, the target dies, and its body "
    r"turns to dust\. The curse lasts until removed by the remove curse spell or "
    r"other magic\.",
    re.IGNORECASE,
)


def semantic_persistent_save_names_2014(monster: SourceMonster2014) -> tuple[str, ...]:
    """Find candidate actions by printed semantics, never monster or ability identity."""
    try:
        sections = source_sections_2014(monster.source_actions)
        return tuple(name for name, text in sections.items() if _SEMANTIC.search(text))
    except Exception:
        logger.exception("Failed persistent-save semantic scan for %s.", monster.id)
        raise


def source_proven_persistent_save_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> PersistentSaveEffectProof2014 | None:
    try:
        if attack.source_complete or attack.kind != "melee" or attack.on_hit_save_effect:
            return None
        text = source_sections_2014(monster.source_actions).get(attack.name, "")
        match = _PATTERN.fullmatch(text)
        if match is None:
            return None
        values = match.groupdict()
        base = attack.damage
        extra = {
            "average": int(values["extra_avg"]),
            "dice_count": int(values["extra_n"]),
            "dice_size": int(values["extra_s"]),
            "bonus": 0,
            "type": values["extra_type"].lower(),
        }
        if (
            (attack.attack_bonus, attack.reach_ft) !=
            (int(values["hit"]), int(values["reach"]))
            or (base.average, base.dice_count, base.dice_size, base.bonus, base.type) !=
            (int(values["base_avg"]), int(values["base_n"]),
             int(values["base_s"]), int(values["base_bonus"]), values["base_type"].lower())
            or attack.on_hit_damage != [extra]
            or int(values["loss_avg"]) !=
            int(values["loss_n"]) * (int(values["loss_s"]) + 1) // 2
            or attack.control_effect is not None
            or attack.ongoing_damage_effect is not None
            or attack.conditional_damage
            or attack.conditional_attack_advantage
        ):
            return None
        effect_id = re.sub(r"[^a-z0-9]+", "-", values["curse"].lower()).strip("-")
        return PersistentSaveEffectProof2014(
            save_ability=values["ability"].lower(), dc=int(values["dc"]),
            effect_id=effect_id, curse_id=effect_id,
            cannot_regain_hit_points=True,
            allowed_removal_action_ids=["remove-curse"],
            delayed_max_hp_reduction_delay_hours=int(values["hours"]),
            delayed_max_hp_reduction_dice_count=int(values["loss_n"]),
            delayed_max_hp_reduction_dice_size=int(values["loss_s"]),
            delayed_max_hp_reduction_zero_kills=True,
        )
    except Exception:
        logger.exception("Failed persistent-save source proof for %s/%s.", monster.id, attack.id)
        raise


def source_completed_persistent_save_2014(
    monster: SourceMonster2014, attack: SourceAttack2014,
) -> SourceAttack2014:
    try:
        proof = source_proven_persistent_save_2014(monster, attack)
        if proof is None:
            return attack
        return attack.model_copy(update={
            "source_complete": True,
            "on_hit_save_effect": proof.model_dump(),
        })
    except Exception:
        logger.exception("Failed persistent-save completion for %s/%s.", monster.id, attack.id)
        raise
