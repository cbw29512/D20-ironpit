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

  window.IRON_PIT_BROWSER_ARENA_MAP = { buildStandardMap };
})();
