(() => {
  "use strict";

  function buildStandardMap() {
    try {
      return {
        id: "iron-pit-standard-vtt",
        width_squares: 24,
        height_squares: 16,
        cell_size_ft: 5,
      };
    } catch (error) {
      console.error("Failed to build standard browser Iron Pit map", { error });
      throw error;
    }
  }

  function buildHeroDeploymentZone() {
    try {
      return {
        x: 0,
        y: 2,
        width_squares: 8,
        height_squares: 12,
        front_edge: "east",
      };
    } catch (error) {
      console.error("Failed to build browser hero deployment zone", { error });
      throw error;
    }
  }

  function buildMonsterDeploymentZone() {
    try {
      return {
        x: 16,
        y: 2,
        width_squares: 8,
        height_squares: 12,
        front_edge: "west",
      };
    } catch (error) {
      console.error("Failed to build browser monster deployment zone", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ARENA_MAP = {
    buildStandardMap,
    buildHeroDeploymentZone,
    buildMonsterDeploymentZone,
  };
})();
