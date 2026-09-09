(() => {
  "use strict";

  function support() {
    try {
      const api = window.IRON_PIT_BROWSER_GRID_MOVEMENT_SUPPORT;
      if (!api) throw new Error("Grid movement support API is not loaded.");
      return api;
    } catch (error) {
      console.error("Failed to load browser grid movement support", { error });
      throw error;
    }
  }

  function pathSearch() {
    try {
      const api = window.IRON_PIT_BROWSER_GRID_PATH_SEARCH;
      if (!api) throw new Error("Grid path-search API is not loaded.");
      return api;
    } catch (error) {
      console.error("Failed to load browser grid path search", { error });
      throw error;
    }
  }

  function affordableLegalPrefix(map, mover, members, route, movementBudgetFt) {
    try {
      const api = support();
      let spent = 0;
      let lastLegalIndex = -1;
      let lastLegalCost = 0;
      for (let index = 0; index < route.length; index += 1) {
        const destination = route[index];
        const stepCost = api.movementStepCostFt(map, mover, destination, members);
        if (stepCost == null) {
          throw new Error(`Path search returned an illegal step at ${destination.x},${destination.y}.`);
        }
        if (spent + stepCost > movementBudgetFt) break;
        spent += stepCost;
        if (api.occupantsAt(mover, destination, members).length === 0) {
          lastLegalIndex = index;
          lastLegalCost = spent;
        }
      }
      if (lastLegalIndex < 0) return { path: [], cost: 0 };
      return { path: route.slice(0, lastLegalIndex + 1), cost: lastLegalCost };
    } catch (error) {
      console.error("Failed to truncate browser grid route", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  function planToward(map, mover, target, members, desiredDistanceFt, movementBudgetFt) {
    try {
      if (desiredDistanceFt < 0 || movementBudgetFt < 0) {
        throw new Error("Movement distance values cannot be negative.");
      }
      const api = support();
      const helpers = {
        position: api.position,
        occupantsAt: api.occupantsAt,
        movementStepCostFt: api.movementStepCostFt,
      };
      const route = pathSearch().searchPathToward(
        map,
        mover,
        target,
        members,
        desiredDistanceFt,
        helpers,
      );
      const targetPosition = api.position(target);
      const routeGoalPosition = route.length ? route[route.length - 1] : api.position(mover);
      const routeGoalDistance = api.geometry().footprintDistanceFt(
        routeGoalPosition,
        mover.state.template.size,
        targetPosition,
        target.state.template.size,
      );
      const prefix = affordableLegalPrefix(map, mover, members, route, movementBudgetFt);
      const finalPosition = prefix.path.length ? prefix.path[prefix.path.length - 1] : api.position(mover);
      const finalDistance = api.geometry().footprintDistanceFt(
        finalPosition,
        mover.state.template.size,
        targetPosition,
        target.state.template.size,
      );
      return {
        path: prefix.path,
        movement_cost_ft: prefix.cost,
        final_distance_ft: finalDistance,
        goal_reachable: routeGoalDistance <= desiredDistanceFt,
      };
    } catch (error) {
      console.error("Failed to plan browser grid movement", {
        mover: mover.combatant_id,
        target: target.combatant_id,
        error,
      });
      throw error;
    }
  }

  function canPassThrough(mover, occupant) {
    try {
      return support().canPassThrough(mover, occupant);
    } catch (error) {
      console.error("Failed browser passage proxy", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  function creatureSpaceIsDifficult(mover, occupant) {
    try {
      return support().creatureSpaceIsDifficult(mover, occupant);
    } catch (error) {
      console.error("Failed browser difficult-space proxy", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  function movementStepCostFt(map, mover, destination, members) {
    try {
      return support().movementStepCostFt(map, mover, destination, members);
    } catch (error) {
      console.error("Failed browser movement-cost proxy", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_MOVEMENT = {
    canPassThrough,
    creatureSpaceIsDifficult,
    movementStepCostFt,
    planToward,
  };
})();
