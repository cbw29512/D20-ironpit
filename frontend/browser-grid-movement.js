(() => {
  "use strict";

  const SIZE_RANK = { tiny: 0, small: 1, medium: 2, large: 3, huge: 4, gargantuan: 5 };

  function geometry() {
    try {
      const api = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
      if (!api) throw new Error("Grid geometry API is not loaded.");
      return api;
    } catch (error) {
      console.error("Failed to load browser grid geometry", { error });
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

  function conditionRules() {
    try {
      return window.IRON_PIT_BROWSER_CONDITION_RULES || {
        incapacitated: (state) => state.is_unconscious,
      };
    } catch (error) {
      console.error("Failed to load browser condition rules", { error });
      throw error;
    }
  }

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
      if (conditionRules().incapacitated(occupant.state) || occupant.state.template.size === "tiny") return true;
      return Math.abs(SIZE_RANK[mover.state.template.size] - SIZE_RANK[occupant.state.template.size]) >= 2;
    } catch (error) {
      console.error("Failed to evaluate creature-space passage", {
        mover: mover.combatant_id,
        occupant: occupant.combatant_id,
        error,
      });
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
      return members.filter((occupant) => occupant.combatant_id !== mover.combatant_id
        && occupant.state.position
        && geometry().overlaps(
          destination,
          mover.state.template.size,
          occupant.state.position,
          occupant.state.template.size,
        ));
    } catch (error) {
      console.error("Failed to resolve occupied grid destination", {
        mover: mover.combatant_id,
        destination,
        error,
      });
      throw error;
    }
  }

  function movementStepCostFt(map, mover, destination, members) {
    try {
      if (!geometry().inBounds(map, destination, mover.state.template.size)) return null;
      let cost = map.cell_size_ft || 5;
      for (const occupant of occupantsAt(mover, destination, members)) {
        if (!canPassThrough(mover, occupant)) return null;
        if (creatureSpaceIsDifficult(mover, occupant)) cost = (map.cell_size_ft || 5) * 2;
      }
      return cost;
    } catch (error) {
      console.error("Failed to calculate grid movement step cost", {
        mover: mover.combatant_id,
        error,
      });
      throw error;
    }
  }

  function affordableLegalPrefix(map, mover, members, route, movementBudgetFt) {
    try {
      let spent = 0;
      let lastLegalIndex = -1;
      let lastLegalCost = 0;
      for (let index = 0; index < route.length; index += 1) {
        const destination = route[index];
        const stepCost = movementStepCostFt(map, mover, destination, members);
        if (stepCost == null) throw new Error(`Path search returned an illegal step at ${destination.x},${destination.y}.`);
        if (spent + stepCost > movementBudgetFt) break;
        spent += stepCost;
        if (occupantsAt(mover, destination, members).length === 0) {
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
      const helpers = { position, occupantsAt, movementStepCostFt };
      const route = pathSearch().searchPathToward(
        map, mover, target, members, desiredDistanceFt, helpers,
      );
      const prefix = affordableLegalPrefix(map, mover, members, route, movementBudgetFt);
      const finalPosition = prefix.path.length ? prefix.path[prefix.path.length - 1] : position(mover);
      const finalDistance = geometry().footprintDistanceFt(
        finalPosition,
        mover.state.template.size,
        position(target),
        target.state.template.size,
      );
      return {
        path: prefix.path,
        movement_cost_ft: prefix.cost,
        final_distance_ft: finalDistance,
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

  window.IRON_PIT_BROWSER_GRID_MOVEMENT = {
    canPassThrough,
    creatureSpaceIsDifficult,
    movementStepCostFt,
    planToward,
  };
})();
