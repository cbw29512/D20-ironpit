"""Source-neutral offensive barrier placement in one-square Iron Pit combat.

Schema: card owns the creation save, material, sections and spell/resource cost.
State: the placed wall and resolved saving throws belong to this encounter.
A section uses its first-side cells to represent the printed 1-foot wall space;
forced displacement is logged, not applied, under the locked arena contract.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.action_economy import is_available
from app.combat.persistent_barrier_geometry import validate_barrier_layout
from app.combat.resources import action_resource_available
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.persistent_barriers import GridBarrierEdge, PersistentBarrierAction

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BarrierOffenseChoice:
    action: PersistentBarrierAction
    sections: tuple[tuple[GridBarrierEdge, ...], ...]
    affected_ids: tuple[str, ...]
    expected_damage: float


def _layouts(action, center, width, height):
    """Enumerate 10-foot straight sections through one authoritative cell."""
    length = action.section_length_ft // 5
    for axis in ("x", "y"):
        for section_count in range(action.min_sections, action.max_sections + 1):
            total = length * section_count
            for before in range(total):
                for side in (-1, 1):
                    coordinates = []
                    for offset in range(total):
                        x = center.x + (offset - before if axis == "x" else 0)
                        y = center.y + (offset - before if axis == "y" else 0)
                        next_x = x if axis == "x" else x + side
                        next_y = y + side if axis == "x" else y
                        coordinates.append((x, y, next_x, next_y))
                    # Validate coordinates BEFORE constructing bounded GridPosition.
                    if not all(0 <= x < width and 0 <= y < height
                               and 0 <= nx < width and 0 <= ny < height
                               for x, y, nx, ny in coordinates):
                        continue
                    first = [(x, y) for x, y, _, _ in coordinates]
                    edges = [
                        GridBarrierEdge(
                            first=GridPosition(x=x, y=y),
                            second=GridPosition(x=nx, y=ny),
                        )
                        for x, y, nx, ny in coordinates
                    ]
                    yield (
                        tuple(tuple(edges[n:n + length]) for n in range(0, total, length)),
                        set(first),
                    )


def choose_offensive_barrier(actor: EncounterCombatant, setup: EncounterSetup):
    """Rank only legal walls with a printed on-creation damage save."""
    try:
        if not is_available(actor.state, "action") or setup.map_definition is None:
            return None
        opponents = setup.monsters if actor.side == "heroes" else setup.heroes
        friends = setup.heroes if actor.side == "heroes" else setup.monsters
        living = [member for member in opponents if member.state.position is not None
                  and member.state.is_alive and not member.state.is_dead
                  and member.state.current_hp > 0]
        if not living:
            return None
        others = [*opponents, *friends]
        existing_edges = {
            edge.canonical_key()
            for wall in setup.persistent_barriers for section in wall.sections
            if not section.destroyed
            for edge in section.edges
        }
        best = None
        for action in actor.state.template.persistent_barrier_actions:
            save = action.on_creation_save
            if (save is None or not save.damage_dice_count
                    or action.action_cost != "action"
                    or not action_resource_available(actor.state, action)):
                continue
            for enemy in living:
                for sections, occupied in _layouts(
                    action, enemy.state.position,
                    setup.map_definition.width_squares,
                    setup.map_definition.height_squares,
                ):
                    if any(edge.canonical_key() in existing_edges
                           for panel in sections for edge in panel):
                        continue
                    try:
                        validate_barrier_layout(
                            action, [list(panel) for panel in sections], actor, setup,
                        )
                    except ValueError:
                        continue
                    hit = tuple(member.combatant_id for member in others
                                if member.state.position is not None
                                and (member.state.position.x, member.state.position.y) in occupied
                                and member.state.is_alive and not member.state.is_dead
                                and member.state.current_hp > 0)
                    enemies_hit = sum(member.combatant_id in hit for member in living)
                    if not enemies_hit:
                        continue
                    allies_hit = len(hit) - enemies_hit
                    average = save.damage_dice_count * (save.damage_dice_size + 1) / 2
                    score = average * (enemies_hit - 2 * allies_hit)
                    if score <= 0:
                        continue
                    choice = BarrierOffenseChoice(action, sections, hit, score)
                    if best is None or (score, -len(sections)) > (
                        best.expected_damage, -len(best.sections)
                    ):
                        best = choice
        return best
    except Exception:
        logger.exception("Offensive barrier choice failed for %s", actor.combatant_id)
        raise

