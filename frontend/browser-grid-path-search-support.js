(() => {
  "use strict";

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
      return left.f - right.f || left.alignment - right.alignment
        || left.cost - right.cost || left.x - right.x || left.y - right.y;
    } catch (error) {
      console.error("Failed to compare A* nodes", { left, right, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_PATH_SEARCH_SUPPORT = {
    geometry,
    keyOf,
    reconstruct,
    scoreLess,
    compareNodes,
  };
})();
