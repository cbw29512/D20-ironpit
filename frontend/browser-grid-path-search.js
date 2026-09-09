(() => {
  "use strict";

  // A* route-search behavior is adapted from BattleCast ai-movement.ts at
  // ffe036c758f18e772a808f538fe3baa845b9bcc0 (MIT, Bartosz Jedrzejewski).
  // See docs/BATTLECAST_MOVEMENT_PROVENANCE.md for attribution details.
  const OFFSETS = [
    [0, -1], [-1, 0], [1, 0], [0, 1],
    [-1, -1], [1, -1], [-1, 1], [1, 1],
  ];

  function support() {
    try {
      const api = window.IRON_PIT_BROWSER_GRID_PATH_SEARCH_SUPPORT;
      if (!api) throw new Error("Grid path-search support API is not loaded.");
      return api;
    } catch (error) {
      console.error("Failed to load browser path-search support", { error });
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
      console.error("Failed to validate diagonal grid movement", {
        mover: mover.combatant_id,
        error,
      });
      throw error;
    }
  }

  function searchPathToward(map, mover, target, members, desiredDistanceFt, helpers) {
    try {
      if (desiredDistanceFt < 0) throw new Error("Desired distance cannot be negative.");
      const api = support();
      const grid = api.geometry();
      const start = helpers.position(mover);
      const targetPosition = helpers.position(target);
      const startKey = api.keyOf(start);
      const startDistance = grid.footprintDistanceFt(
        start,
        mover.state.template.size,
        targetPosition,
        target.state.template.size,
      );
      const costs = new Map([[startKey, 0]]);
      const previous = new Map();
      const open = [{
        f: Math.max(0, startDistance - desiredDistanceFt),
        alignment: Math.abs(start.x - targetPosition.x) + Math.abs(start.y - targetPosition.y),
        cost: 0,
        x: start.x,
        y: start.y,
      }];
      let bestKey = startKey;
      let bestScore = [Math.max(0, startDistance - desiredDistanceFt), startDistance, 0, start.x, start.y];

      while (open.length) {
        open.sort(api.compareNodes);
        const node = open.shift();
        const currentKey = `${node.x},${node.y}`;
        if (node.cost !== costs.get(currentKey)) continue;
        const current = { x: node.x, y: node.y };
        const distance = grid.footprintDistanceFt(
          current,
          mover.state.template.size,
          targetPosition,
          target.state.template.size,
        );
        const finalLegal = helpers.occupantsAt(mover, current, members).length === 0;
        const score = [Math.max(0, distance - desiredDistanceFt), distance, node.cost, node.x, node.y];
        if (finalLegal && api.scoreLess(score, bestScore)) {
          bestKey = currentKey;
          bestScore = score;
        }
        if (finalLegal && distance <= desiredDistanceFt) {
          return api.reconstruct(currentKey, previous);
        }

        for (const [dx, dy] of OFFSETS) {
          const destination = { x: current.x + dx, y: current.y + dy };
          if (destination.x < 0 || destination.y < 0) continue;
          const stepCost = helpers.movementStepCostFt(map, mover, destination, members);
          if (stepCost == null || !diagonalAllowed(
            map,
            mover,
            current,
            destination,
            members,
            helpers,
          )) continue;
          const nextCost = node.cost + stepCost;
          const nextKey = api.keyOf(destination);
          if (nextCost >= (costs.get(nextKey) ?? Number.POSITIVE_INFINITY)) continue;
          costs.set(nextKey, nextCost);
          previous.set(nextKey, currentKey);
          const nextDistance = grid.footprintDistanceFt(
            destination,
            mover.state.template.size,
            targetPosition,
            target.state.template.size,
          );
          open.push({
            f: nextCost + Math.max(0, nextDistance - desiredDistanceFt),
            alignment: Math.abs(destination.x - targetPosition.x) + Math.abs(destination.y - targetPosition.y),
            cost: nextCost,
            x: destination.x,
            y: destination.y,
          });
        }
      }
      return api.reconstruct(bestKey, previous);
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
