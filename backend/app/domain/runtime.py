from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.combatants import CombatantTemplate, DamageType
from app.domain.events import BattleEvent
from app.domain.modifiers import CombatModifier
from app.domain.positions import GridPosition
from app.domain.resources import ResourceState

ConditionTiming = Literal["source_turn_start", "source_turn_end", "target_turn_start", "target_turn_end"]
TimedTurnBehavior = Literal["normal", "skip_turn"]


class ConcentrationState(BaseModel):
    source_effect_id: str
    source_name: str


class GrappleSource(BaseModel):
    source_id: str
    source_name: str
    escape_dc: int = Field(ge=1, le=40)
    escape_ability_options: list[str] = Field(default_factory=lambda: ["strength", "dexterity"])


class DeferredEffectState(BaseModel):
    effect_id: str
    source_id: str
    source_effect_id: str
    target_id: str
    armed_round: int = Field(ge=1)


class TimedEffect(BaseModel):
    effect_id: str
    source_id: str
    source_effect_id: str | None = None
    source_name: str | None = None
    condition_id: str | None = None
    applied_round: int | None = Field(default=None, ge=1)
    expires_round: int | None = Field(default=None, ge=1)
    expires_at_start_of_source_turn: bool = True
    expiry_timing: ConditionTiming | None = None
    repeat_save_ability: str | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None
    allowed_removal_action_ids: list[str] = Field(default_factory=list)
    turn_behavior: TimedTurnBehavior = "normal"
    ends_on_damage: bool = False
    ends_if_source_incapacitated: bool = False
    ends_if_source_dead: bool = False
    owned_damage_resistances: list[DamageType] = Field(default_factory=list)
    owned_magical_condition_immunities: list[str] = Field(default_factory=list)
    # Generic source-owned defense: magical effects cannot reduce this target's
    # speed while the owning timed effect is active. Nonmagical speed penalties
    # remain valid, preserving source semantics rather than spell-name logic.
    prevents_magical_speed_reduction: bool = False

    @model_validator(mode="after")
    def validate_lifecycle(self) -> "TimedEffect":
        repeat_fields = (self.repeat_save_ability, self.repeat_save_dc, self.repeat_save_timing)
        if any(item is not None for item in repeat_fields) and not all(item is not None for item in repeat_fields):
            raise ValueError("Timed effect repeat save requires ability, DC, and timing together.")
        if self.expires_round is not None and self.applied_round is not None and self.expires_round <= self.applied_round:
            raise ValueError("Timed effect expiry round must follow its applied round.")
        if self.expiry_timing is not None:
            self.expires_at_start_of_source_turn = self.expiry_timing == "source_turn_start"
        return self


class DemoRoster(BaseModel):
    fighter: CombatantTemplate
    monster: CombatantTemplate


class ArenaRoster(BaseModel):
    characters: list[CombatantTemplate]
    monsters: list[CombatantTemplate]


class CombatantState(BaseModel):
    template: CombatantTemplate
    current_hp: int
    max_hp_bonus: int = Field(default=0, ge=0)
    temporary_hp: int = Field(default=0, ge=0)
    position: GridPosition | None = None
    initiative_roll: int | None = None
    initiative_total: int | None = None
    is_alive: bool = True
    is_unconscious: bool = False
    is_stable: bool = False
    is_dead: bool = False
    exhaustion_level: int = Field(default=0, ge=0, le=6)
    death_save_successes: int = Field(default=0, ge=0, le=3)
    death_save_failures: int = Field(default=0, ge=0, le=3)
    action_available: bool = True
    bonus_action_available: bool = True
    reaction_available: bool = True
    turn_terminated: bool = False
    turn_termination_reason: str | None = None
    heroic_inspiration: bool = False
    movement_remaining_ft: int = Field(default=0, ge=0)
    resources: list[ResourceState] = Field(default_factory=list)
    active_effect_ids: list[str] = Field(default_factory=list)
    active_buff_effect_ids: list[str] = Field(default_factory=list)
    opening_buff_spell_id: str | None = None
    grapple_sources: list[GrappleSource] = Field(default_factory=list)
    timed_effects: list[TimedEffect] = Field(default_factory=list)
    deferred_effects: list[DeferredEffectState] = Field(default_factory=list)
    active_modifiers: list[CombatModifier] = Field(default_factory=list)
    concentration: ConcentrationState | None = None
    survival_save_uses: dict[str, int] = Field(default_factory=dict)
    pending_survival_save_logs: list[str] = Field(default_factory=list)
    feature_last_turn_keys: dict[str, str] = Field(default_factory=dict)
    spell_slot_expended_turn_key: str | None = None
    temporary_damage_resistances: list[DamageType] = Field(default_factory=list)
    rage_expires_round: int | None = Field(default=None, ge=1)
    rage_max_round: int | None = Field(default=None, ge=1)


class BattlefieldState(BaseModel):
    map_definition: object | None = None
    starting_distance_ft: int = Field(default=5, ge=0)
    distance_ft: int = Field(default=5, ge=0)


class BattleState(BaseModel):
    combatants: list[CombatantState] = Field(default_factory=list)
    battlefield: BattlefieldState = Field(default_factory=BattlefieldState)
    events: list[BattleEvent] = Field(default_factory=list)
