from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.actions import ActionCost, ConditionName, ConditionTiming
from app.domain.debuffs import DebuffCounter
from app.domain.environment_contexts import EmittedEnvironmentContext
from app.domain.friendly_combat_auras import (
    TimedFriendlyRecoveryAura,
    TimedFriendlyWeaponDamageAura,
)
from app.domain.timed_aura_components import (
    TimedEmanationDamage, TimedHostileConditionAura,
    TimedFriendlyCoverAura, TimedFriendlySaveAura,
)
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.movement import MovementModeGrant
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)


class MeleeHitRetaliation(BaseModel):
    """Damage a creature that hits the source with a melee attack roll inside the printed reach."""

    range_ft: int = Field(default=5, ge=5, le=15)
    dice_count: int = Field(ge=1, le=40)
    dice_size: int = Field(default=8, ge=2, le=100)
    damage_type: DamageType


class TimedSelfBuffAction(BaseModel):
    """Declarative timed self effect composed from universal combat primitives."""

    id: str
    name: str
    action_cost: ActionCost = "action"
    activation_timing: Literal["action", "start_turn", "passive"] = "action"
    start_turn_max_current_hp: int | None = Field(default=None, ge=1)
    start_turn_roll_die_size: int | None = Field(default=None, ge=2, le=100)
    start_turn_roll_minimum: int | None = Field(default=None, ge=1)
    ends_at_full_hp: bool = False
    target_policy: Literal["normal", "nearest_visible_creature"] = "normal"
    resource_id: str | None = None
    resource_cost: int = Field(default=1, ge=1, le=200)
    duration_rounds: int | None = Field(default=None, ge=1, le=600)
    condition_ids: list[ConditionName] = Field(default_factory=list)
    damage_resistances: list[DamageType] = Field(default_factory=list)
    melee_hit_retaliation: MeleeHitRetaliation | None = None
    debuff_counters: list[DebuffCounter] = Field(default_factory=list)
    saving_throw_advantage_grants: list[SavingThrowAdvantageGrant] = Field(default_factory=list)
    movement_mode_grants: list[MovementModeGrant] = Field(default_factory=list)
    friendly_save_advantage_aura: TimedFriendlySaveAura | None = None
    friendly_cover_aura: TimedFriendlyCoverAura | None = None
    friendly_weapon_damage_aura: TimedFriendlyWeaponDamageAura | None = None
    friendly_recovery_aura: TimedFriendlyRecoveryAura | None = None
    hostile_start_turn_condition_aura: TimedHostileConditionAura | None = None
    start_turn_emanation_damage: TimedEmanationDamage | None = None
    emitted_environment_contexts: list[EmittedEnvironmentContext] = Field(default_factory=list)
    spell_save_dc_bonus: int = Field(default=0, ge=0, le=10)
    spell_attack_advantage: bool = False
    modifier_effects: list[SpellModifierEffect] = Field(default_factory=list)
    concentration: bool = False
    ends_if_source_incapacitated: bool = False
    ends_if_source_dead: bool = False
    expiry_timing: ConditionTiming | None = "source_turn_start"
    priority: int = 0
    selection_group: str | None = None
    selection_strategy: Literal["priority", "incoming-damage"] = "priority"
    animation: str = "buff"

    @model_validator(mode="after")
    def validate_on_turn_activation(self) -> "TimedSelfBuffAction":
        try:
            if self.activation_timing == "passive":
                # Passive source data is discovered directly, never cast/spent.
                if sum(aura is not None for aura in (
                    self.hostile_start_turn_condition_aura, self.friendly_save_advantage_aura,
                )) != 1:
                    raise ValueError("Passive activation requires exactly one condition or friendly-save aura.")
                if self.resource_id or self.concentration or self.duration_rounds is not None or self.ends_if_source_incapacitated:
                    raise ValueError("Passive condition auras cannot own activation resources or a source timer.")
                if any((self.condition_ids, self.damage_resistances, self.melee_hit_retaliation,
                    self.debuff_counters, self.saving_throw_advantage_grants, self.movement_mode_grants,
                    self.friendly_cover_aura,
                    self.friendly_weapon_damage_aura, self.friendly_recovery_aura,
                    self.start_turn_emanation_damage, self.emitted_environment_contexts,
                    self.spell_save_dc_bonus, self.spell_attack_advantage, self.modifier_effects)):
                    raise ValueError("Passive condition aura cannot silently omit activation-owned effects.")
                aura = self.hostile_start_turn_condition_aura
                if aura is not None and aura.condition_expiry_timing is None:
                    raise ValueError("Passive condition auras require explicit target expiry.")
            trigger_fields = (self.start_turn_max_current_hp, self.start_turn_roll_die_size, self.start_turn_roll_minimum)
            if any(item is not None for item in trigger_fields) and self.activation_timing != "start_turn":
                raise ValueError("Start-turn buff triggers require start_turn activation timing.")
            if (self.start_turn_roll_die_size is None) != (self.start_turn_roll_minimum is None):
                raise ValueError("Start-turn roll triggers require both die size and minimum roll.")
            if self.start_turn_roll_die_size is not None and self.start_turn_roll_minimum > self.start_turn_roll_die_size:
                raise ValueError("Start-turn roll minimum cannot exceed die size.")
            if self.action_cost == "reaction":
                raise ValueError("Timed self-buff Actions currently require an on-turn Action or Bonus Action.")
            if len(set(self.condition_ids)) != len(self.condition_ids):
                raise ValueError("Timed self-buff condition ids must be unique.")
            if len(set(self.damage_resistances)) != len(self.damage_resistances):
                raise ValueError("Timed self-buff damage resistances must be unique.")
            if self.selection_strategy == "incoming-damage" and (
                not self.selection_group or len(self.damage_resistances) != 1
            ):
                raise ValueError("Incoming-damage selection requires a group and one resistance type.")
            counter_keys = {
                (item.debuff_id, item.source_scope, item.mode, item.movement_cost_ft)
                for item in self.debuff_counters
            }
            if len(counter_keys) != len(self.debuff_counters):
                raise ValueError("Timed self-buff debuff counters must be unique.")
            grant_keys = {
                (
                    item.source_id,
                    tuple(item.abilities),
                    item.requires_magical_effect,
                    item.requires_spell_effect,
                    tuple(item.source_creature_types),
                )
                for item in self.saving_throw_advantage_grants
            }
            if len(grant_keys) != len(self.saving_throw_advantage_grants):
                raise ValueError("Timed self-buff saving-throw Advantage grants must be unique.")
            if not (
                self.condition_ids
                or self.damage_resistances
                or self.debuff_counters
                or self.saving_throw_advantage_grants
                or self.movement_mode_grants
                or self.friendly_save_advantage_aura is not None
                or self.friendly_cover_aura is not None
                or self.friendly_weapon_damage_aura is not None
                or self.friendly_recovery_aura is not None
                or self.hostile_start_turn_condition_aura is not None
                or self.start_turn_emanation_damage is not None
                or self.emitted_environment_contexts
                or self.melee_hit_retaliation is not None
                or self.spell_save_dc_bonus
                or self.spell_attack_advantage
                or self.modifier_effects
                or self.target_policy != "normal"
                or self.concentration
            ):
                raise ValueError("Timed self-buff requires at least one combat effect.")
            return self
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Timed self-buff schema validation failed for %s.", self.id)
            raise RuntimeError("Timed self-buff schema could not be validated.") from exc
