(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;

  function bestAreaDestination(actor, setup, action, reachable) {
    try {
      if (!action.area) throw new Error(`${action.id} does not define area geometry.`);
      const members = new Map([...setup.heroes, ...setup.monsters]
        .map((member) => [member.combatant_id, member]));
      const candidates = [];
      for (const plan of reachable) {
        const placements = A().legalPlacements(actor, setup, action.area, action.range, plan.destination);
        for (const placement of placements) {
          const expectedValue = placement.targetIds.reduce(
            (sum, id) => sum + O().saveAction(members.get(id), action),
            0,
          );
          candidates.push({ destinationPlan: plan, placement, expectedValue });
        }
      }
      candidates.sort((left, right) => right.expectedValue - left.expectedValue
        || right.placement.targetIds.length - left.placement.targetIds.length
        || left.destinationPlan.movement_cost_ft - right.destinationPlan.movement_cost_ft
        || left.destinationPlan.destination.x - right.destinationPlan.destination.x
        || left.destinationPlan.destination.y - right.destinationPlan.destination.y
        || left.placement.targetIds.join("|").localeCompare(right.placement.targetIds.join("|")));
      return candidates[0] || null;
    } catch (error) {
      console.error("Failed browser reachable area-position scoring", {
        actor: actor?.combatant_id,
        action: action?.id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_AREA_MOVEMENT_CHOICE = { bestAreaDestination };
})();
