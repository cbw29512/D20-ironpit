from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.actions import SavingThrowAction
from app.domain.legendary_actions import (
    LegendaryAcBuffSpec,
    LegendaryActionOption,
    LegendaryHealSpec,
)
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)
RESOURCE_ID = "legendary-actions"
_PIT_BANNED_LEGENDARY = frozenset({"teleport", "plane shift"})


def _attack_id(monster: SourceMonster2014, source_attack_id: str) -> str:
    return f"2014-{monster.id}-{source_attack_id}".replace("--", "-")


def _label(name: str) -> str:
    return name.split(" (Costs", 1)[0].strip().casefold()


def _save_action(payload: dict[str, object]) -> SavingThrowAction:
    area = payload.get("area")
    if not isinstance(area, dict):
        raise ValueError("Legendary save action requires area geometry.")
    control = payload.get("failure_control_effect") or {}
    if not isinstance(control, dict):
        control = {}
    condition_id = control.get("condition_id")
    return SavingThrowAction(
        id=str(payload["id"]),
        name=str(payload["name"]),
        save_ability=str(payload["save_ability"]),
        dc=int(payload["dc"]),
        range_ft=int(payload.get("range_ft") or 0),
        area=AreaTargeting(
            shape=str(area.get("shape") or "emanation"),
            origin=str(area.get("origin") or "self"),
            radius_ft=int(area.get("radius_ft") or payload.get("range_ft") or 0),
        ),
        damage_dice_count=int(payload.get("damage_dice_count") or 0),
        damage_dice_size=int(payload.get("damage_dice_size") or 6),
        damage_bonus=int(payload.get("damage_bonus") or 0),
        damage_type=payload.get("damage_type"),
        success_damage=str(payload.get("success_damage") or "none"),
        failed_save_timed_effect=(
            FailedSaveTimedEffect(effect_id=str(condition_id))
            if condition_id else None
        ),
        animation=str(payload.get("animation") or "save-effect"),
    )


def _compile_source_option(monster: SourceMonster2014, raw: object) -> LegendaryActionOption | None:
    if not isinstance(raw, dict):
        raise ValueError(f"{monster.name} legendary action is not a structured object.")
    name = str(raw.get("name") or "")
    if _label(name) in _PIT_BANNED_LEGENDARY:
        return None
    kind = str(raw.get("kind") or "")
    cost = int(raw.get("cost") or 1)
    option_id = str(raw.get("id") or _label(name).replace(" ", "-"))
    if kind == "attack":
        attack_id = str(raw.get("attack_id") or "")
        if not attack_id:
            raise ValueError(f"{monster.name} legendary attack {name!r} is missing attack_id.")
        return LegendaryActionOption(
            id=option_id, name=name, cost=cost, kind="attack",
            attack_id=_attack_id(monster, attack_id),
        )
    if kind == "save":
        save = raw.get("save_action")
        if not isinstance(save, dict):
            raise ValueError(f"{monster.name} legendary save {name!r} is missing save_action.")
        return LegendaryActionOption(
            id=option_id, name=name, cost=cost, kind="save",
            save_action=_save_action(save),
        )
    if kind == "ability_check":
        return LegendaryActionOption(
            id=option_id, name=name, cost=cost, kind="check",
            check_ability=str(raw.get("check_ability") or "wisdom"),
            check_skill=str(raw.get("check_skill") or "perception"),
        )
    return None


def _compile_named_unsupported(monster: SourceMonster2014, name: str) -> LegendaryActionOption | None:
    label = _label(name)
    if label in _PIT_BANNED_LEGENDARY:
        return None
    if label == "shimmering shield":
        return LegendaryActionOption(
            id="shimmering-shield",
            name="Shimmering Shield",
            cost=2,
            kind="ac_buff",
            ac_buff=LegendaryAcBuffSpec(ac_bonus=2, range_ft=60),
        )
    if label == "heal self":
        return LegendaryActionOption(
            id="heal-self",
            name="Heal Self",
            cost=3,
            kind="heal",
            heal=LegendaryHealSpec(dice_count=2, dice_size=8, healing_bonus=2),
        )
    return None


def legendary_action_options_2014(monster: SourceMonster2014) -> list[LegendaryActionOption]:
    """Compile every printed legendary option except pit-banned teleport/plane shift."""
    try:
        options: list[LegendaryActionOption] = []
        for raw in monster.legendary_actions:
            option = _compile_source_option(monster, raw)
            if option is not None:
                options.append(option)
        compiled = {_label(item.name) for item in options}
        for name in monster.unsupported_legendary_action_names:
            if _label(name) in compiled:
                continue
            option = _compile_named_unsupported(monster, name)
            if option is not None:
                options.append(option)
        return options
    except Exception:
        logger.exception("Failed to compile 2014 legendary actions for %s.", monster.name)
        raise


def supports_legendary_actions_2014(monster: SourceMonster2014) -> bool:
    try:
        if not monster.legendary_action_names and not monster.legendary_action_uses:
            return not monster.legendary_actions and not monster.unsupported_legendary_action_names
        options = legendary_action_options_2014(monster)
        printed = [
            name for name in monster.legendary_action_names
            if _label(name) not in _PIT_BANNED_LEGENDARY
        ]
        bound = {_label(item.name) for item in options}
        return bool(options) and all(_label(name) in bound for name in printed)
    except ValueError:
        return False
    except Exception:
        logger.exception("Failed to classify 2014 legendary support for %s.", monster.name)
        raise
