(() => {
  "use strict";
  // Browser peer of backend/app/combat/spell_target_groups.py.
  function legalGroup(targets, maximumPairDistanceFt) {
    try {
      if (maximumPairDistanceFt == null || targets.length < 2) return true;
      const distance = window.IRON_PIT_BROWSER_STATE?.distance;
      if (typeof distance !== "function") {
        throw new Error("Shared spell target geometry is unavailable.");
      }
      for (let first = 0; first < targets.length; first += 1) {
        for (let second = first + 1; second < targets.length; second += 1) {
          if (distance(targets[first], targets[second]) > maximumPairDistanceFt) {
            return false;
          }
        }
      }
      return true;
    } catch (error) {
      console.error("Shared spell target geometry failed.", { error });
      throw error;
    }
  }

  function chooseGroup(ranked, cap, maximumPairDistanceFt) {
    try {
      if (!Number.isInteger(cap) || cap < 1) {
        throw new Error("A save-spell target cap must be positive.");
      }
      if (maximumPairDistanceFt == null) return ranked.slice(0, cap);
      // Search highest capacity first, preserving existing rank order for ties.
      function firstLegal(size, start = 0, selected = []) {
        for (let i = start; i <= ranked.length - (size - selected.length); i += 1) {
          const next = [...selected, ranked[i]];
          if (!legalGroup(next, maximumPairDistanceFt)) continue;
          if (next.length === size) return next;
          const result = firstLegal(size, i + 1, next);
          if (result) return result;
        }
        return null;
      }
      for (let size = Math.min(cap, ranked.length); size >= 1; size -= 1) {
        const legal = firstLegal(size);
        if (legal) return legal;
      }
      return [];
    } catch (error) {
      console.error("Cannot choose a source-legal spell target group.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_TARGET_GROUPS = { legalGroup, chooseGroup };
})();
