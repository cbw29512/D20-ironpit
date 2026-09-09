(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const SIZE_RANK = { tiny: 0, small: 1, medium: 2, large: 3, huge: 4, gargantuan: 5 };
  const OFFSETS = [-1, 0, 1].flatMap((dx) => [-1, 0, 1].map((dy) => [dx, dy]))
    .filter(([dx, dy]) => dx || dy);
  const keyOf = (position) => `${position.x},${position.y}`;

  function position(member) {
    try {
      if (!member.state.position) throw new Error(`${member.combatant_id} has no authoritative grid position.`);
      return member.state.position;
    } catch (error) {
      console.error("Failed to read combatant grid position", { id: member.combatant_id, error });
      throw error;
    }
  }

  function canPassThrough(mover, occupant) {
    try {
      if (mover.combatant_id === occupant.combatant_id || mover.side === occupant.side) return true;
      if (Q().incapacitated(occupant.state) || occupant.state.template.size === "tiny") return true;
      return Math.abs(SIZE_RANK[mover.state.template.size] - SIZE_RANK[occupant.state.template.size]) >= 2;
    } catch (error) {
      console.error("Failed to evaluate creature-space passage", { mover: mover.combatant_id, occupant: occupant.combatant_id, error });
      throw error;
    }
  }

  function creatureSpaceIsDifficult(mover, occupant) {
    try {
      if (mover.combatant_id === occupant.combatant_id || mover.side === occupant.side) return false;
      return occupant.state.template.size !== "tiny";
    } catch (error) {
      console.error("Failed to evaluate creature-space movement cost", { error });
      throw error;
    }
  }

  function occupantsAt(mover, destination, members) {
    try {
      return members.filter((occupant) => occupant.combatant_id !== mover.combatant_id && occupant.state.position
        && G().overlaps(destination, mover.state.template.size, occupant.state.position, occupant.state.template.size));
    } catch (error) {
      console.error("Failed to resolve occupied grid destination", { mover: mover.combatant_id, destination, error });
      throw error;
    }
  }

  function movementStepCostFt(map, mover, destination, members) {
    try {
      if (!G().inBounds(map, destination, mover.state.template.size)) return null;
      let cost = map.cell_size_ft || 5;
      for (const occupant of occupantsAt(mover, destination, members)) {
        if (!canPassThrough(mover, occupant)) return null;
        if (creatureSpaceIsDifficult(mover, occupant)) cost = (map.cell_size_ft || 5) * 2;
      }
      return cost;
    } catch (error) {
      console.error("Failed to calculate grid movement step cost", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  function reconstruct(endKey, previous) {
    const path = [];
    let cursor = endKey;
    while (previous.has(cursor)) {
      const [x, y] = cursor.split(",").map(Number);
      path.push({ x, y });
      cursor = previous.get(cursor);
    }
    return path.reverse();
  }

  function planToward(map, mover, target, members, desiredDistanceFt, movementBudgetFt) {
    try {
      if (desiredDistanceFt < 0 || movementBudgetFt < 0) throw new Error("Movement distance values cannot be negative.");
      const start = position(mover), targetPosition = position(target), startKey = keyOf(start);
      const costs = new Map([[startKey, 0]]), previous = new Map();
      const open = [{ cost: 0, x: start.x, y: start.y }];
      let bestKey = startKey;
      let bestScore = [G().footprintDistanceFt(start, mover.state.template.size, targetPosition, target.state.template.size), 0, start.x, start.y];

      while (open.length) {
        open.sort((a, b) => a.cost - b.cost || a.x - b.x || a.y - b.y);
        const currentNode = open.shift(), currentKey = `${currentNode.x},${currentNode.y}`;
        if (currentNode.cost !== costs.get(currentKey) || currentNode.cost > movementBudgetFt) continue;
        const current = { x: currentNode.x, y: currentNode.y };
        const finalLegal = occupantsAt(mover, current, members).length === 0;
        const distance = G().footprintDistanceFt(current, mover.state.template.size, targetPosition, target.state.template.size);
        const score = [distance, currentNode.cost, current.x, current.y];
        const better = score.some((value, index) => value < bestScore[index] && score.slice(0, index).every((v, i) => v === bestScore[i]));
        if (finalLegal && better) { bestKey = currentKey; bestScore = score; }
        if (finalLegal && distance <= desiredDistanceFt) {
          return { path: reconstruct(currentKey, previous), movement_cost_ft: currentNode.cost, final_distance_ft: distance };
        }

        for (const [dx, dy] of OFFSETS) {
          const destination = { x: current.x + dx, y: current.y + dy };
          if (destination.x < 0 || destination.y < 0) continue;
          const step = movementStepCostFt(map, mover, destination, members);
          if (step == null) continue;
          const nextCost = currentNode.cost + step, nextKey = keyOf(destination);
          if (nextCost > movementBudgetFt || nextCost >= (costs.get(nextKey) ?? Number.POSITIVE_INFINITY)) continue;
          costs.set(nextKey, nextCost); previous.set(nextKey, currentKey);
          open.push({ cost: nextCost, x: destination.x, y: destination.y });
        }
      }
      return { path: reconstruct(bestKey, previous), movement_cost_ft: costs.get(bestKey), final_distance_ft: bestScore[0] };
    } catch (error) {
      console.error("Failed to plan browser grid movement", { mover: mover.combatant_id, target: target.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_MOVEMENT = {
    canPassThrough, creatureSpaceIsDifficult, movementStepCostFt, planToward,
  };
})();
