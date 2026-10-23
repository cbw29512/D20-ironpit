"""Semantic 2014 variable-head binding; runtime resolution is source-neutral."""
from __future__ import annotations

import html
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.variable_heads import VariableHeadProfile

logger = logging.getLogger(__name__)
_WORD_NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                 "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
_HAS_HEADS = re.compile(r"\bhas (?P<count>\w+) heads?\b", re.IGNORECASE)
_SEVER = re.compile(
    r"takes (?P<damage>\d+) or more damage in a single turn, one of its heads dies",
    re.IGNORECASE,
)
_REGROW = re.compile(
    r"grows (?P<count>\w+) heads? for each of its heads that died since its last turn",
    re.IGNORECASE,
)
_BLOCK = re.compile(
    r"unless it has taken (?P<kind>[a-z]+) damage since its last turn",
    re.IGNORECASE,
)
_HEAL = re.compile(
    r"regains (?P<amount>\d+) hit points for each head regrown this way",
    re.IGNORECASE,
)
_EXTRA_REACTION = re.compile(
    r"extra reaction.+?only for opportunity attacks", re.IGNORECASE,
)
_HEAD_MULTIATTACK = re.compile(
    r"makes as many (?P<attack>[A-Za-z][A-Za-z -]*?) attacks as it has heads",
    re.IGNORECASE,
)


def _plain(value: str | None) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    return " ".join(without_tags.split())


def _number(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        if value.casefold() not in _WORD_NUMBERS:
            raise ValueError(f"Unsupported printed head count: {value!r}")
        return _WORD_NUMBERS[value.casefold()]


def semantic_variable_head_sections_2014(
    monster: SourceMonster2014,
) -> tuple[tuple[str, str], tuple[str, str]] | None:
    """Locate the lifecycle and OA clauses by meaning, never card identity/name."""
    traits = {name: _plain(body) for name, body in source_sections_2014(monster.source_traits).items()}
    reaction_sections = traits
    all_traits = " ".join(traits.values())
    all_source = " ".join((all_traits, _plain(monster.source_actions), _plain(monster.source_reactions)))
    lifecycle = next(
        ((name, all_source) for name, body in traits.items()
         if _HAS_HEADS.search(body) and _SEVER.search(body)),
        None,
    )
    reaction = next(
        ((name, body) for name, body in reaction_sections.items()
         if _EXTRA_REACTION.search(body)),
        None,
    )
    any_signal = bool(
        _HAS_HEADS.search(monster.source_traits or "")
        or _SEVER.search(monster.source_traits or "")
        or _REGROW.search(monster.source_traits or "")
        or _EXTRA_REACTION.search(monster.source_traits or "")
        or _HEAD_MULTIATTACK.search(_plain(monster.source_actions))
    )
    if not any_signal:
        return None
    complete_lifecycle = all((
        _HAS_HEADS.search(all_source), _SEVER.search(all_source),
        _REGROW.search(all_source), _BLOCK.search(all_source), _HEAL.search(all_source),
    ))
    if lifecycle is None or reaction is None or not complete_lifecycle:
        found = {
            "initial": bool(_HAS_HEADS.search(all_source)),
            "sever": bool(_SEVER.search(all_source)),
            "regrow": bool(_REGROW.search(all_source)),
            "block": bool(_BLOCK.search(all_source)),
            "heal": bool(_HEAL.search(all_source)),
            "reaction": reaction is not None,
        }
        raise ValueError(f"Printed variable-head card has incomplete semantic clauses: {found}")
    if _HEAD_MULTIATTACK.search(_plain(monster.source_actions)) is None:
        raise ValueError("Printed variable-head card lacks a head-count Multiattack clause.")
    return lifecycle, reaction


def variable_head_profile_2014(monster: SourceMonster2014) -> VariableHeadProfile | None:
    try:
        sections = semantic_variable_head_sections_2014(monster)
        if sections is None:
            return None
        (source_name, body), (reaction_name, _) = sections
        initial = _HAS_HEADS.search(body)
        sever = _SEVER.search(body)
        regrow = _REGROW.search(body)
        blocker = _BLOCK.search(body)
        healing = _HEAL.search(body)
        if None in {initial, sever, regrow, blocker, healing}:
            raise ValueError("Variable-head semantic match lost a required source clause.")
        return VariableHeadProfile(
            source_name=source_name,
            reaction_source_name=reaction_name,
            initial_heads=_number(initial["count"]),
            sever_damage_threshold=int(sever["damage"]),
            heads_per_regrowth=_number(regrow["count"]),
            healing_per_regrown_head=int(healing["amount"]),
            regrowth_blocking_damage_types=[blocker["kind"].casefold()],
        )
    except Exception:
        logger.exception("Failed semantic variable-head binding for %s.", monster.id)
        raise


def variable_head_trait_names_2014(monster: SourceMonster2014) -> set[str]:
    try:
        profile = variable_head_profile_2014(monster)
        return {profile.source_name, profile.reaction_source_name} if profile else set()
    except ValueError:
        logger.info("Variable-head source remains fail-closed for %s.", monster.id)
        return set()
