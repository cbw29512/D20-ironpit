from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.combat.action_economy import is_available
from app.content.monster_creature_types import is_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup

ChannelChoiceKind = Literal["turn-undead", "divine-spark-heal", "divine-spark-damage"]


@dataclass(frozen=True)
class ChannelDivinityChoice:
    kind: ChannelChoiceKind
    targets: tuple[EncounterCombatant, ...]


def _distance(left: EncounterCombatant, right: EncounterCombatant) -> int:
    return abs(left.position_ft - right.position_ft)


def _uses(member: EncounterCombatant, resource_id: str) -> int:
    resource = next((item for item in member.state.resources if item.id == resource_id), None)
    return resource.current_uses if resource is not None else 0


def _living(side: list[EncounterCombatant]) -> list[EncounterCombatant]:
    return [member for member in side if member.state.is_alive and not member.state.is_dead]


def _downed_other_ally(cleric: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    allies = setup.heroes if cleric.side == "heroes" else setup.monsters
    legal = [
        ally for ally in _living(allies)
        if ally.combatant_id != cleric.combatant_id and ally.state.current_hp == 0 and _distance(cleric, ally) <= 30
    ]
    return max(legal, key=lambda ally: ally.state.death_save_failures, default=None)


def _undead_targets(cleric: EncounterCombatant, setup: EncounterSetup) -> tuple[EncounterCombatant, ...]:
    enemies = setup.monsters if cleric.side == "heroes" else setup.heroes
    legal = [
        enemy for enemy in _living(enemies)
        if _distance(cleric, enemy) <= 30 and is_creature_type(enemy.state.template, "undead")
    ]
    return tuple(sorted(legal, key=lambda enemy: (_distance(cleric, enemy), enemy.combatant_id)))


def _nearest_enemy(cleric: EncounterCombatant, setup: EncounterSetup) -> EncounterCombatant | None:
    enemies = setup.monsters if cleric.side == "heroes" else setup.heroes
    legal = [enemy for enemy in _living(enemies) if _distance(cleric, enemy) <= 30]
    return min(legal, key=lambda enemy: (_distance(cleric, enemy), enemy.combatant_id), default=None)


def choose_channel_divinity(cleric: EncounterCombatant, setup: EncounterSetup) -> ChannelDivinityChoice | None:
    """Rescue if needed, otherwise control Undead, and conserve damage Spark while spell slots remain."""
    if not is_available(cleric.state, "action") or _uses(cleric, "channel-divinity") < 1:
        return None
    downed = _downed_other_ally(cleric, setup)
    if downed is not None and not any(item.id.startswith("spell-slot-") and item.current_uses for item in cleric.state.resources):
        return ChannelDivinityChoice("divine-spark-heal", (downed,))
    undead = _undead_targets(cleric, setup)
    if undead:
        return ChannelDivinityChoice("turn-undead", undead)
    if any(item.id.startswith("spell-slot-") and item.current_uses for item in cleric.state.resources):
        return None
    enemy = _nearest_enemy(cleric, setup)
    return ChannelDivinityChoice("divine-spark-damage", (enemy,)) if enemy is not None else None
