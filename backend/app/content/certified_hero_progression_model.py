from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.domain.character_builds import CharacterBuildProfile
from app.domain.models import CombatantTemplate
from app.domain.rulesets import RulesetId

ProfileBuilder = Callable[[], CharacterBuildProfile]
ProfileLevelBuilder = Callable[[int], CharacterBuildProfile]
TemplateLevelBuilder = Callable[[int], CombatantTemplate]


@dataclass(frozen=True)
class CertifiedHeroProgression:
    class_id: str
    ruleset: RulesetId
    template_builder: TemplateLevelBuilder
    profile_builders: tuple[ProfileBuilder, ...] = ()
    profile_level_builder: ProfileLevelBuilder | None = None
    max_level: int | None = None

    @property
    def levels(self) -> range:
        count = self.max_level if self.max_level is not None else len(self.profile_builders)
        return range(1, count + 1)

    def profile(self, level: int) -> CharacterBuildProfile:
        try:
            if level not in self.levels:
                raise ValueError(f"{self.class_id} level {level} is not registered for certification.")
            if self.profile_level_builder is not None:
                return self.profile_level_builder(level)
            return self.profile_builders[level - 1]()
        except Exception:
            raise
