(() => {
  "use strict";

  // Iron Pit's fixed, one-creature-per-cell arena disregards forced displacement.
  // Damage, saving throws, and conditions are resolved by their original callers.
  function ignoredForcedMovement(distanceFt, direction) {
    try {
      if (!Number.isInteger(distanceFt) || distanceFt < 0 || distanceFt % 5) {
        throw new Error("Forced movement distance must be a nonnegative multiple of 5 feet.");
      }
      return 0;
    } catch (error) {
      console.error(`Invalid ${direction} forced displacement.`, error);
      throw error;
    }
  }

  function pushStraightAway(mover, source, setup, distanceFt) {
    return ignoredForcedMovement(distanceFt, "push");
  }

  function pullStraightToward(mover, source, setup, distanceFt) {
    return ignoredForcedMovement(distanceFt, "pull");
  }

  window.IRON_PIT_BROWSER_FORCED_MOVEMENT = { pullStraightToward, pushStraightAway };
})();
