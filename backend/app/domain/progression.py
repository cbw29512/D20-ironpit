from __future__ import annotations

from pydantic import BaseModel, Field


class ProgressionCombatFeatures(BaseModel):
    """Level/subclass combat flags that should stay out of core stat-block shape."""

    critical_hit_minimum: int = Field(default=20, ge=2, le=20)
    initiative_advantage: bool = False
    athletics_advantage: bool = False
    danger_sense: bool = False
    reckless_attack: bool = False
    frenzy: bool = False
    fast_movement_bonus_ft: int = Field(default=0, ge=0)
    mindless_rage: bool = False
    instinctive_pounce_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    great_weapon_fighting: bool = False
    indomitable_bonus: int = Field(default=0, ge=0, le=20)
    tactical_master_sap_weapon_ids: list[str] = Field(default_factory=list)
    sneak_attack_d6: int = Field(default=0, ge=0, le=10)
    critical_move_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
    tactical_shift_fraction: float = Field(default=0.0, ge=0.0, le=1.0)
