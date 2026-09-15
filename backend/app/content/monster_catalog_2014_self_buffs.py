from __future__ import annotations

import html
import re
import unicodedata

from app.domain.self_buffs import SelfBuffAction


def _plain(value: str | None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def self_buff_actions_2014(source_actions: str | None) -> list[SelfBuffAction]:
    results: list[SelfBuffAction] = []
    for paragraph in re.findall(r"<p>(.*?)</p>", source_actions or "", re.I | re.S):
        heading_match = re.search(r"<strong>(.*?)</strong>", paragraph, re.I | re.S)
        if heading_match is None:
            continue
        heading = _plain(heading_match.group(1)).rstrip(".")
        text = _plain(paragraph)
        if not re.search(r"Until the end of its next turn", text, re.I):
            continue
        ac = re.search(r"gains? a \+(\d+) bonus to its AC", text, re.I)
        save = re.search(r"has advantage on (\w+) saving throws", text, re.I)
        bonus_attack = re.search(r"can use its ([A-Za-z ]+) attack as a bonus action", text, re.I)
        if not all((ac, save, bonus_attack)):
            continue
        name = re.sub(r"\s*\(Recharge\s+[^)]+\)\s*$", "", heading, flags=re.I).strip()
        action_id = _slug(name)
        results.append(SelfBuffAction(
            id=action_id,
            name=name,
            resource_id=action_id,
            armor_class_bonus=int(ac.group(1)),
            save_advantage_abilities=[save.group(1).lower()],
            bonus_action_attack_id=_slug(bonus_attack.group(1)),
        ))
    return results
