from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import AbilityName, ConditionTiming, GrappleSource
from app.domain.combatants import CombatantTemplate, DamageType
from app.domain.grid import BattleMapDefinition, GridPosition
from app.domain.modifiers import CombatModifier, ConcentrationState
from app.domain.movement import DifficultTerrainScope
from app.domain.persistent_spell_attacks import PersistentSpellAttackState

TimedTurnBehavior = Literal["normal", "forced_retreat"]


class ResourceState(BaseModel):
    id: str
    name: str
    current_uses: int = Field(ge=0)
    max_uses: int = Field(ge=0)


class DeferredEffectState(BaseModel):
    """Fresh per-fight state for one armed deferred source/target relationship."""

    source_id: str
    target_id: str
    armed_round: int = Field(ge=1)


class TimedEffect(BaseModel):
    effect_id: str
    source_id: str
    source_effect_id: str | None = None
    applied_round: int | None = Field(default=None, ge=1)
    expires_round: int | None = Field(default=None, ge=1)
    expires_at_start_of_source_turn: bool = True
    expiry_timing: ConditionTiming | None = None
    repeat_save_ability: AbilityName | None = None
    repeat_save_dc: int | None = Field(default=None, ge=1, le=40)
    repeat_save_timing: ConditionTiming | None = None
    allowed_removal_action_ids: list[str] = Field(default_factory=list)
    turn_behavior: TimedTurnBehavior = "normal"
    suppress_action: bool = False
    suppress_bonus_action: bool = False
    suppress_reactions: bool = False
    suppress_movement: bool = False
    ends_on_damage: bool = False
    ends_if_source_incapacitated: bool = False
    ends_if_source_dead: bool = False
    # Universal source ownership for temporary typed resistances.  This lets a
    # timed effect clean up only the resistance contribution it owns while an
    # overlapping effect that grants the same type remains active.
    owned_damage_resistances: list[DamageType] = Field(default_factory=list)
    # Conditions prevented only when the incoming effect is magical. This is
    # intentionally distinct from blanket condition immunity: source data must
    # identify the incoming effect as magical before this defense applies.
    owned_magical_condition_immunities: list[str] = Field(default_factory=list)
    difficult_terrain_bypass_scope: DifficultTerrainScope | None = None
    zero_hp_replacement_hp: int = Field(default=0, ge=0)
    prevents_nondamage_instant_death: bool = False

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
    persistent_spell_attacks: list[PersistentSpellAttackState] = Field(default_factory=list)
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
    map_definition: BattleMapDefinition | None = None
    # Migration-only scalar distance fields. Remove after all canonical paths consume grid positions.
    starting_distance_ft: int = Field(default=5, ge=0)
    distance_ft: int = Field(default=5, ge=0)