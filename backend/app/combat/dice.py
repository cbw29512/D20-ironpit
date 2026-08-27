from __future__ import annotations

import logging
import secrets
from collections import deque
from typing import Protocol

logger = logging.getLogger(__name__)


class DiceProvider(Protocol):
    def roll(self, sides: int) -> int: ...


class SecureDiceProvider:
    """Production dice backed by the operating system CSPRNG."""

    def roll(self, sides: int) -> int:
        try:
            if sides < 2:
                raise ValueError("A die must have at least two sides.")
            return secrets.randbelow(sides) + 1
        except Exception as exc:
            logger.exception("Secure die roll failed for d%s.", sides)
            raise RuntimeError(f"Unable to roll d{sides}.") from exc


class FixedDiceProvider:
    """Deterministic dice for unit tests; never use for production fights."""

    def __init__(self, rolls: list[int]) -> None:
        try:
            if not rolls:
                raise ValueError("At least one fixed roll is required.")
            self._rolls: deque[int] = deque(rolls)
        except Exception as exc:
            logger.exception("Failed to initialize fixed dice provider.")
            raise

    def roll(self, sides: int) -> int:
        try:
            if not self._rolls:
                raise RuntimeError("Fixed dice sequence is exhausted.")
            value = self._rolls.popleft()
            if not 1 <= value <= sides:
                raise ValueError(f"Fixed value {value} is invalid for d{sides}.")
            return value
        except Exception:
            logger.exception("Fixed die roll failed for d%s.", sides)
            raise
