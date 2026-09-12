(() => {
  "use strict";

  const OFFSETS = [
    [0, -1], [-1, 0], [1, 0], [0, 1],
    [-1, -1], [1, -1], [-1, 1], [1, 1],
  ];
  const S = () => window.IRON_PIT_BROWSER_GRID_MOVEMENT_SUPPORT;
  const keyOf = (position) => `${position.x},${position.y}`;

  function reconstruct(endKey, previous) {
    const path = [];
    let cursor = endKey;
    while (previous.has(cursor)) {
      const [x, y] = cursor.split(",").map(Number);
      path.push({ x, y });
      cursor = previous.get(cursor);
    }
    path.reverse();
    return path;
  }

  function diagonalAllowed(map, mover, current, destination, members) {
    const dx = destination.x - current.x, dy = destination.y - current.y;
    if (dx === 0 || dy === 0) return true;
    const sideX = { x: current.x + dx, y: current.y };
    const sideY = { x: current.x, y: current.y + dy };
    return S().movementStepCostFt(map, mover, sideX, members) != null
      || S().movementStepCostFt(map, mover, sideY, members) != null;
  }

  function reachableDestinations(map, mover, members, movementBudgetFt) {
    try {
      if (movementBudgetFt < 0) throw new Error("Movement budget cannot be negative.");
      const start = S().position(mover), startKey = keyOf(start);
      const costs = new Map([[startKey, 0]]), previous = new Map();
      const queue = [{ cost: 0, x: start.x, y: start.y }], plans = [];
      while (queue.length) {
        queue.sort((a, b) => a.cost - b.cost || a.x - b.x || a.y - b.y);
        const node = queue.shift(), current = { x: node.x, y: node.y }, currentKey = keyOf(current);
        if (node.cost !== costs.get(currentKey) || node.cost > movementBudgetFt) continue;
        if (!S().occupantsAt(mover, current, members).length) {
          plans.push({ destination: current, path: reconstruct(currentKey, previous), movement_cost_ft: node.cost });
        }
        for (const [dx, dy] of OFFSETS) {
          const destination = { x: current.x + dx, y: current.y + dy };
          if (destination.x < 0 || destination.y < 0) continue;
          const stepCost = S().movementStepCostFt(map, mover, destination, members);
          if (stepCost == null || !diagonalAllowed(map, mover, current, destination, members)) continue;
          const nextCost = node.cost + stepCost, nextKey = keyOf(destination);
          if (nextCost > movementBudgetFt || nextCost >= (costs.get(nextKey) ?? Number.POSITIVE_INFINITY)) continue;
          costs.set(nextKey, nextCost); previous.set(nextKey, currentKey);
          queue.push({ cost: nextCost, x: destination.x, y: destination.y });
        }
      }
      return plans.sort((a, b) => a.movement_cost_ft - b.movement_cost_ft
        || a.destination.x - b.destination.x || a.destination.y - b.destination.y);
    } catch (error) {
      console.error("Failed browser reachable-grid search", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_REACHABLE = { reachableDestinations };
})();
