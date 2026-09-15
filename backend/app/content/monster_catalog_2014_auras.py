from __future__ import annotations

import html
import logging
import re
import unicodedata

from app.domain.auras import StartTurnAura

logger = logging.getLogger(__name__)
_STENCH = re.compile(
    r"Stench\.\s*Any creature that starts its turn within (?P<range>\d+) feet of the [^.]+ "
    r"must succeed on a DC (?P<dc>\d+) Constitution saving throw or be poisoned until the start of its next turn\. "
    r"On a successful saving throw, the creature is immune to the [^.]+ stench for 24 hours\.",
    re.I,
)
_SAVE = re.compile(
    r"DC\s+(?P<dc>\d+)\s+"
    r"(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw",
    re.I,
)
_RADIUS = re.compile(r"\b(?P<feet>\d+)\s*[-‐‑‒–—]?\s*foot\s+radius\b", re.I)
_CONDITION_UNTIL_NEXT_TURN = re.compile(
    r"or\s+be\s+(?P<condition>[A-Za-z]+)\s+until\s+(?:the\s+)?start\s+of\s+(?:its|the target'?s)\s+next\s+turn",
    re.I,
)


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = html.unescape(text).replace("\u00ad", "")
    return re.sub(r"\s+", " ", text).strip()


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _duration_rounds(text: str) -> int | None:
    match = re.search(r"\blasts?\s+for\s+(\d+)\s+(minute|minutes|round|rounds)\b", text, re.I)
    if match is None:
        return None
    amount, unit = match.groups()
    value = int(amount)
    return value * 10 if unit.lower().startswith("minute") else value


def start_turn_auras_2014(source_traits: str | None) -> list[StartTurnAura]:
    try:
        if not source_traits or "Stench." not in source_traits:
            return []
        match = _STENCH.search(_plain(source_traits))
        if match is None:
            raise ValueError("Stench source text is not a supported start-turn aura shape.")
        return [StartTurnAura(
            id="stench", name="Stench", range_ft=int(match.group("range")),
            save_ability="constitution", save_dc=int(match.group("dc")),
            failure_condition_id="poisoned", success_grants_source_immunity=True,
        )]
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Failed to parse passive 2014 start-turn aura.")
        raise RuntimeError("Passive 2014 aura parsing failed.") from exc


def activated_start_turn_auras_2014(source_actions: str | None) -> list[StartTurnAura]:
    """Parse limited-use self-centered areas that save when a creature starts its turn inside."""
    try:
        results: list[StartTurnAura] = []
        paragraphs = re.findall(r"<p>(.*?)</p>", source_actions or "", re.I | re.S)
        for paragraph in paragraphs:
            heading_match = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
            if heading_match is None:
                continue
            heading = _plain(heading_match.group(1)).rstrip(".")
            use_match = re.search(r"\((\d+)\s*/\s*Day\)", heading, re.I)
            text = _plain(paragraph)
            if use_match is None or not re.search(r"starts its turn in that area", text, re.I):
                continue
            radius = _RADIUS.search(text)
            duration = _duration_rounds(text)
            save = _SAVE.search(text)
            condition = _CONDITION_UNTIL_NEXT_TURN.search(text)
            missing = [
                key for key, value in (
                    ("radius", radius), ("duration", duration), ("save", save), ("condition", condition),
                ) if value is None
            ]
            if missing:
                raise ValueError(
                    f"Activated start-turn aura is missing parsed {','.join(missing)}: {heading!r}; text={text!r}."
                )
            name = re.sub(r"\s*\(\d+\s*/\s*Day\)\s*$", "", heading, flags=re.I).strip()
            aura_id = _slug(name)
            results.append(StartTurnAura(
                id=aura_id,
                name=name,
                range_ft=int(radius.group("feet")),
                save_ability=save.group("ability").lower(),
                save_dc=int(save.group("dc")),
                failure_condition_id=condition.group("condition").lower(),
                failure_expiry_timing="target_turn_start",
                failure_duration_rounds=1,
                failure_blocks_reactions=bool(re.search(r"can(?:not|'t) take reactions", text, re.I)),
                failure_action_bonus_exclusive=bool(re.search(
                    r"either an action or a bonus action on its turn, not both", text, re.I,
                )),
                activation_cost="action",
                activation_duration_rounds=duration,
                resource_id=aura_id,
                resource_cost=1,
                area_lightly_obscured=bool(re.search(r"area is lightly obscured", text, re.I)),
                spreads_around_corners=bool(re.search(r"spreads around corners", text, re.I)),
                dispersed_by_strong_wind=bool(re.search(r"strong wind disperses it", text, re.I)),
            ))
        return results
    except (TypeError, ValueError):
        raise
    except Exception as exc:
        logger.exception("Failed to parse activated 2014 start-turn auras.")
        raise RuntimeError("Activated 2014 aura parsing failed.") from exc
