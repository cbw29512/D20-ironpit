from __future__ import annotations

from functools import lru_cache
import json
import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

logger = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).with_name("data")
_CATALOG_PATH = _DATA_DIR / "srd_5_1_monsters_catalog.json"
_MANIFEST_PATH = _DATA_DIR / "srd_5_1_monsters_source_manifest.json"


class SourceDamage2014(BaseModel):
    model_config = ConfigDict(extra="ignore")
    average: int = Field(ge=0)
    dice_count: int = Field(ge=0)
    dice_size: int = Field(ge=2)
    bonus: int = 0
    type: str | None = None


class SourceAttack2014(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    kind: Literal["melee", "ranged"]
    attack_bonus: int
    damage: SourceDamage2014
    reach_ft: int = 5
    normal_range_ft: int | None = None
    long_range_ft: int | None = None
    source_complete: bool = True
    conditional_damage: list[object] = Field(default_factory=list)
    conditional_attack_advantage: list[object] = Field(default_factory=list)
    on_hit_damage: list[object] = Field(default_factory=list)
    on_hit_save_effect: object | None = None
    on_hit_contested_movement: object | None = None
    ongoing_damage_effect: object | None = None
    control_effect: object | None = None
    resource_id: str | None = None
    breakable_restraint: object | None = None
    charge_profile: object | None = None


class SourceMonster2014(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    ruleset: Literal["2014"]
    size: str
    creature_type: str
    armor_class: int = Field(ge=1)
    max_hp: int = Field(ge=1)
    speed: dict[str, int]
    abilities: dict[str, int]
    saving_throws: dict[str, int] = Field(default_factory=dict)
    skills: dict[str, int] = Field(default_factory=dict)
    damage_resistances: list[str] = Field(default_factory=list)
    damage_immunities: list[str] = Field(default_factory=list)
    damage_vulnerabilities: list[str] = Field(default_factory=list)
    condition_immunities: list[str] = Field(default_factory=list)
    unsupported_defense_text: list[str] = Field(default_factory=list)
    challenge_rating: str | None = None
    attacks: list[SourceAttack2014] = Field(default_factory=list)
    saving_throw_actions: list[object] = Field(default_factory=list)
    death_trigger_actions: list[object] = Field(default_factory=list)
    healing_actions: list[object] = Field(default_factory=list)
    limited_action_uses: dict[str, int] = Field(default_factory=dict)
    innate_spellcasting: object | None = None
    spellcasting: object | None = None
    multiattack_slots: list[list[str]] = Field(default_factory=list)
    multiattack_policy: object | None = None
    multiattack_binding: object | None = None
    zero_hp_prevention: object | None = None
    regeneration: object | None = None
    legendary_action_uses: int = 0
    legendary_actions: list[object] = Field(default_factory=list)
    unsupported_legendary_action_names: list[str] = Field(default_factory=list)
    action_recharges: dict[str, int] = Field(default_factory=dict)
    rest_recharge_action_ids: list[str] = Field(default_factory=list)
    action_names: list[str] = Field(default_factory=list)
    trait_names: list[str] = Field(default_factory=list)
    reaction_names: list[str] = Field(default_factory=list)
    legendary_action_names: list[str] = Field(default_factory=list)


@lru_cache(maxsize=1)
def load_monster_source_2014() -> tuple[SourceMonster2014, ...]:
    try:
        manifest = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
        rows = TypeAdapter(list[SourceMonster2014]).validate_json(_CATALOG_PATH.read_text(encoding="utf-8"))
        expected = int(manifest["monster_count"])
        ids = {row.id for row in rows}
        if manifest.get("ruleset") != "2014" or expected != 327:
            raise ValueError("Pinned 2014 source manifest is not the expected corpus.")
        if len(rows) != expected or len(ids) != expected:
            raise ValueError("Pinned 2014 monster corpus must contain 327 unique records.")
        return tuple(rows)
    except Exception as exc:
        logger.exception("Failed to load pinned 2014 monster source corpus.")
        raise RuntimeError("Pinned 2014 monster source corpus could not be loaded.") from exc
