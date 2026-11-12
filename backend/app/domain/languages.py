"""Immutable language evidence for source-neutral spoken-command eligibility.

A missing or unselected source language is unknown, never an implied Common.
"""
from __future__ import annotations

import logging
import re

from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = logging.getLogger(__name__)
_NAME = re.compile(r"[a-z][a-z' -]{0,48}\Z")


class LanguageProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    spoken: tuple[str, ...] = Field(default_factory=tuple)
    understood: tuple[str, ...] = Field(default_factory=tuple)
    speaks_all: bool = False
    understands_all: bool = False
    unspecified: bool = True

    @model_validator(mode="after")
    def validate_language_evidence(self) -> "LanguageProfile":
        try:
            for values in (self.spoken, self.understood):
                if len(set(values)) != len(values):
                    raise ValueError("Language evidence cannot contain duplicates.")
                if any(not _NAME.fullmatch(name) for name in values):
                    raise ValueError("Language identifiers must be canonical lowercase names.")
            if not set(self.spoken).issubset(self.understood) and not self.understands_all:
                raise ValueError("Every spoken language must also be understood.")
            if self.speaks_all and not self.understands_all:
                raise ValueError("Speaking all languages requires understanding all languages.")
            return self
        except Exception:
            logger.exception("Invalid language profile: source evidence is not canonical.")
            raise
