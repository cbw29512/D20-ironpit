(() => {
  "use strict";

  // A* route-search behavior is adapted from BattleCast ai-movement.ts at
  // ffe036c758f18e772a808f538fe3baa845b9bcc0 (MIT, Bartosz Jedrzejewski).
  // See docs/BATTLECAST_MOVEMENT_PROVENANCE.md for attribution details.
  const OFFSETS = [
    [0, -1], [-1, 0], [1, 0], [0, 1],
    [-1, -1], [1, -1], [-1, 1], [1, 1],
  ];

  function geometry() {
    try {
      const api = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
      if (!api) throw new Error("Grid geometry API is not loaded.");
      return api;
    } catch (error) {
      console.error("Failed to load grid geometry for path search", { error });
      throw error;
    }
  }

  function keyOf(position) {
    try {
      return `${position.x},${position.y}`;
    } catch (error) {
      console.error("Failed to encode grid path key", { position, error });
      throw error;
    }
  }

  function reconstruct(endKey, previous) {
    try {
      const path = [];
      let cursor = endKey;
      while (previous.has(cursor)) {
        const [x, y] = cursor.split(",").map(Number);
        path.push({ x, y });
        cursor = previous.get(cursor);
      }
      return path.reverse();
    } catch (error) {
      console.error("Failed to reconstruct browser grid path", { endKey, error });
      throw error;
    }
  }

  function scoreLess(left, right) {
    try {
      for (let index = 0; index < left.length; index += 1) {
        if (left[index] < right[index]) return true;
        if (left[index] > right[index]) return false;
      }
      return false;
    } catch (error) {
      console.error("Failed to compare path-search scores", { left, right, error });
      throw error;
    }
  }

  function compareNodes(left, right) {
    try {
      return left.f - right.f || left.cost - right.cost || left.x - right.x || left.y - right.y;
    } catch (error) {
      console.error("Failed to compare A* nodes", { left, right, error });
      throw error;
    }
  }

  function diagonalAllowed(map, mover, current, destination, members, helpers) {
    try {
      const dx = destination.x - current.x;
      const dy = destination.y - current.y;
      if (dx === 0 || dy === 0) return true;
      const sideX = { x: current.x + dx, y: current.y };
      const sideY = { x: current.x, y: current.y + dy };
      return helpers.movementStepCostFt(map, mover, sideX, members) != null
        || helpers.movementStepCostFt(map, mover, sideY, members) != null;
    } catch (error) {
      console.error("Failed to validate diagonal grid movement", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  function searchPathToward(map, mover, target, members, desiredDistanceFt, helpers) {
    try {
      if (desiredDistanceFt < 0) throw new Error("Desired distance cannot be negative.");
      const grid = geometry();
      const start = helpers.position(mover);
      const targetPosition = helpers.position(target);
      const startKey = keyOf(start);
      const startDistance = grid.footprintDistanceFt(
        start, mover.state.template.size, targetPosition, target.state.template.size,
      );
      const costs = new Map([[startKey, 0]]);
      const previous = new Map();
      const open = [{
        f: Math.max(0, startDistance - desiredDistanceFt),
        cost: 0,
        x: start.x,
        y: start.y,
      }];
      let bestKey = startKey;
      let bestScore = [Math.max(0, startDistance - desiredDistanceFt), startDistance, 0, start.x, start.y];

      while (open.length) {
        open.sort(compareNodes);
        const node = open.shift();
        const currentKey = `${node.x},${node.y}`;
        if (node.cost !== costs.get(currentKey)) continue;
        const current = { x: node.x, y: node.y };
        const distance = grid.footprintDistanceFt(
          current, mover.state.template.size, targetPosition, target.state.template.size,
        );
        const finalLegal = helpers.occupantsAt(mover, current, members).length === 0;
        const score = [Math.max(0, distance - desiredDistanceFt), distance, node.cost, node.x, node.y];
        if (finalLegal && scoreLess(score, bestScore)) {
          bestKey = currentKey;
          bestScore = score;
        }
        if (finalLegal && distance <= desiredDistanceFt) return reconstruct(currentKey, previous);

        for (const [dx, dy] of OFFSETS) {
          const destination = { x: current.x + dx, y: current.y + dy };
          if (destination.x < 0 || destination.y < 0) continue;
          const stepCost = helpers.movementStepCostFt(map, mover, destination, members);
          if (stepCost == null || !diagonalAllowed(map, mover, current, destination, members, helpers)) continue;
          const nextCost = node.cost + stepCost;
          const nextKey = keyOf(destination);
          if (nextCost >= (costs.get(nextKey) ?? Number.POSITIVE_INFINITY)) continue;
          costs.set(nextKey, nextCost);
          previous.set(nextKey, currentKey);
          const nextDistance = grid.footprintDistanceFt(
            destination, mover.state.template.size, targetPosition, target.state.template.size,
          );
          open.push({
            f: nextCost + Math.max(0, nextDistance - desiredDistanceFt),
            cost: nextCost,
            x: destination.x,
            y: destination.y,
          });
        }
      }
      return reconstruct(bestKey, previous);
    } catch (error) {
      console.error("Full-map browser path search failed", {
        mover: mover.combatant_id,
        target: target.combatant_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_PATH_SEARCH = { searchPathToward };
})();
