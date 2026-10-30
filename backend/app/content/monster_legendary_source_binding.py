from __future__ import annotations

import logging
import re

from app.content.monster_legendary_source_audit import parse_legendary_action_names
from app.content.monster_source_save_candidates import source_save_candidates
from app.domain.capability_attacks import AttackCapabilityDefinition, SaveCapabilityDefinition
from app.domain.legendary_actions import LegendaryActionOption, LegendaryActionPool
from app.domain.save_effects import ConditionEffectDefinition
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

_FEAR = re.compile(
    r"\bcasts Fear,.*?spell save DC\s*(?P<dc>\d+)\)",
    re.IGNORECASE | re.DOTALL,
)
_ATTACK = re.compile(r"\bmakes one (?P<attack>[A-Z][A-Za-z0-9’' -]*?) attack\.", re.IGNORECASE)
_HALF_MOVE_ATTACK = re.compile(
    r"\bmoves up to half its Speed, and it makes one (?P<attack>[A-Z][A-Za-z0-9’' -]*?) attack\.",
    re.IGNORECASE,
)
_ONCE = re.compile(r"can[’']t take this action again until the start of its next turn", re.IGNORECASE)


def _slug(value: str) -> str:
    try:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    except Exception as exc:
        logger.exception("Failed to slug legendary source value %r.", value)
        raise RuntimeError("Legendary source id could not be derived.") from exc


def _sections(text: str, names: list[str]) -> dict[str, str]:
    try:
        starts: list[tuple[str, int, int]] = []
        for name in names:
            match = re.search(rf"\b{re.escape(name)}\.\s*", text)
            if match is None:
                raise ValueError(f"Legendary action heading {name!r} is missing from source.")
            starts.append((name, match.start(), match.end()))
        starts.sort(key=lambda item: item[1])
        return {
            name: text[body_start:(starts[index + 1][1] if index + 1 < len(starts) else len(text))].strip()
            for index, (name, _heading_start, body_start) in enumerate(starts)
        }
    except (TypeError, ValueError):
        logger.exception("Invalid legendary source sections.")
        raise
    except Exception as exc:
        logger.exception("Failed to split legendary source sections.")
        raise RuntimeError("Legendary source sections could not be parsed.") from exc


def _fear_action(monster: str, name: str, body: str) -> SaveCapabilityDefinition | None:
    try:
        match = _FEAR.search(body)
        if match is None:
            return None
        action_id = f"srd-{_slug(monster)}-{_slug(name)}"
        return SaveCapabilityDefinition(
            id=action_id,
            name=name,
            save_ability="wisdom",
            dc=int(match.group("dc")),
            range_ft=0,
            area=AreaTargeting(shape="cone", origin="self", length_ft=30),
            failure_effects=[
                ConditionEffectDefinition(
                    condition="frightened",
                    duration_rounds=10,
                    expiry_timing="target_turn_end",
                    turn_behavior="forced_retreat",
                )
            ],
            magical_effect=True,
            starts_concentration=True,
            concentration_duration_rounds=10,
            animation="fear",
        )
    except (TypeError, ValueError):
        logger.exception("Invalid source-backed Fear legendary action for %s.", monster)
        raise
    except Exception as exc:
        logger.exception("Failed to compile source-backed Fear legendary action for %s.", monster)
        raise RuntimeError("Legendary Fear action could not be compiled.") from exc


def source_legendary_binding(
    row: dict[str, object],
    attacks: list[AttackCapabilityDefinition],
) -> tuple[LegendaryActionPool | None, list[SaveCapabilityDefinition]]:
    """Compile a legendary pool only when every printed option is source-complete."""
    try:
        text = " ".join(str(row.get("legendaryActions", "")).split())
        fingerprints = parse_legendary_action_names(text)
        if not fingerprints:
            return None, []
        uses = int(fingerprints[0].split(":", 1)[1])
        names = fingerprints[1:]
        sections = _sections(text, names)
        fake = dict(row)
        fake["actions"], fake["bonusActions"] = text, ""
        parsed_saves, _resources = source_save_candidates(fake)
        save_by_name = {action.name: action for action in parsed_saves}
        attack_by_name = {attack.name.lower(): attack for attack in attacks}
        options: list[LegendaryActionOption] = []
        extra_saves: list[SaveCapabilityDefinition] = []
        for name in names:
            body = sections[name]
            once = _ONCE.search(body) is not None
            save = save_by_name.get(name) or _fear_action(str(row["name"]), name, body)
            if save is not None:
                if all(existing.id != save.id for existing in extra_saves):
                    extra_saves.append(save)
                options.append(LegendaryActionOption(
                    id=f"srd-{_slug(str(row['name']))}-{_slug(name)}",
                    name=name,
                    kind="saving_throw",
                    action_id=save.id,
                    once_until_owner_turn=once,
                ))
                continue
            move = _HALF_MOVE_ATTACK.search(body)
            attack_match = move or _ATTACK.search(body)
            attack = attack_by_name.get(attack_match.group("attack").lower()) if attack_match else None
            if attack is None:
                return None, []
            options.append(LegendaryActionOption(
                id=f"srd-{_slug(str(row['name']))}-{_slug(name)}",
                name=name,
                kind="attack",
                action_id=attack.id,
                once_until_owner_turn=once,
                movement_before_action="half-speed" if move else None,
            ))
        return LegendaryActionPool(max_uses=uses, options=options), extra_saves
    except (TypeError, ValueError):
        logger.exception("Invalid legendary source binding for %s.", row.get("name"))
        raise
    except Exception as exc:
        logger.exception("Failed legendary source binding for %s.", row.get("name"))
        raise RuntimeError("Legendary source binding could not be compiled.") from exc


__all__ = ["source_legendary_binding"]
