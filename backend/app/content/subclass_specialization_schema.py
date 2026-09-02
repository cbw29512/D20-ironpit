from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SubclassSpecialization:
    class_id: str
    subclass_id: str
    subclass_name: str
    role: str
    ability_priority: tuple[str, ...]
    armor: str | None
    shield: bool
    primary_weapon: str | None
    source_reference: str
    secondary_weapons: tuple[str, ...] = ()
    fighting_style_priority: tuple[str, ...] = ()
    mastery_priority: tuple[str, ...] = ()
    spell_package_id: str | None = None
    focus_item: str | None = None
    feature_choice_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_reference.strip():
            raise ValueError(f"Subclass specialization {self.subclass_id!r} requires a source reference.")
        if self.primary_weapon and self.mastery_priority and self.primary_weapon not in self.mastery_priority:
            raise ValueError(f"Primary weapon {self.primary_weapon!r} must be in the mastery priority.")
        if self.shield and self.primary_weapon is None:
            raise ValueError(f"Shield specialization {self.subclass_id!r} requires a one-handed weapon.")
