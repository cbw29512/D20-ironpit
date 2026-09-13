from __future__ import annotations

import html
import re
import unicodedata


def _plain(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(text).replace("\u00ad", "")).strip()


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def parse_action_recharges(source_actions: str | None) -> dict[str, int]:
    """Return action-id -> minimum successful d6 roll for printed Recharge X-Y actions."""
    recharges: dict[str, int] = {}
    pattern = re.compile(r"^(.*?)\s*\(Recharge\s+([1-6])(?:\s*[\-–—]\s*([1-6]))?\)\.?$", re.I)
    for heading in re.findall(r"<strong>(.*?)</strong>", source_actions or "", re.I | re.S):
        text = _plain(heading).rstrip(".")
        match = pattern.match(text)
        if match is None:
            continue
        name, minimum_text, maximum_text = match.groups()
        minimum = int(minimum_text)
        maximum = int(maximum_text or minimum_text)
        if maximum != 6 or minimum > maximum:
            raise ValueError(f"Unsupported Recharge notation on {text!r}; expected X-6 or 6.")
        action_id = _slug(name.strip())
        if action_id in recharges and recharges[action_id] != minimum:
            raise ValueError(f"Conflicting Recharge notation for action {name.strip()!r}.")
        recharges[action_id] = minimum
    return recharges


def parse_rest_recharge_actions(source_actions: str | None) -> list[str]:
    """Keep non-d6 Recharge-after-rest actions distinct from random Recharge resources."""
    actions: list[str] = []
    pattern = re.compile(r"^(.*?)\s*\(Recharge after a Short or Long Rest\)\.?$", re.I)
    for heading in re.findall(r"<strong>(.*?)</strong>", source_actions or "", re.I | re.S):
        match = pattern.match(_plain(heading).rstrip("."))
        if match:
            actions.append(_slug(match.group(1).strip()))
    return actions
