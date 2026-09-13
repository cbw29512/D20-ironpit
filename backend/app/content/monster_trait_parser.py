from __future__ import annotations

from functools import lru_cache
import logging
import re

logger = logging.getLogger(__name__)
_CONNECTORS = frozenset({"a", "an", "and", "of", "or", "the", "to"})


def _heading_name(value: str) -> str:
    try:
        return re.sub(r"\s*\([^)]*\)$", "", value).strip()
    except Exception:
        logger.exception("Failed to normalize SRD trait heading %r.", value)
        raise


def _is_heading(value: str) -> bool:
    try:
        if not value or len(value) > 80:
            return False
        plain = _heading_name(value)
        if any(mark in plain for mark in ",:;!?"):
            return False
        words = plain.split()
        return bool(words) and all(
            word.lower() in _CONNECTORS or re.fullmatch(r"[A-Z][A-Za-z’'\-]*", word)
            for word in words
        )
    except Exception:
        logger.exception("Failed to classify SRD trait heading %r.", value)
        raise


@lru_cache(maxsize=512)
def _parse_trait_names_cached(text: str) -> tuple[str, ...]:
    try:
        if not text:
            return ()
        names = tuple(
            _heading_name(candidate)
            for sentence in re.split(r"(?<=\.)\s+", text)
            if (candidate := sentence[:-1].strip() if sentence.endswith(".") else "")
            and _is_heading(candidate)
        )
        if not names:
            raise ValueError(f"SRD trait headings could not be parsed from: {text!r}")
        return names
    except Exception:
        logger.exception("Failed to parse SRD trait headings.")
        raise


def parse_trait_names(source_traits: object) -> list[str]:
    try:
        return list(_parse_trait_names_cached(str(source_traits or "").strip()))
    except Exception:
        logger.exception("Failed to resolve cached SRD trait headings.")
        raise
