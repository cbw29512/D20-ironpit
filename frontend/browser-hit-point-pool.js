(() => {
  "use strict";

  const MAX_SAFE = Number.MAX_SAFE_INTEGER;

  function allocateHitPointPool(rolledPool, candidates) {
    try {
      if (!Number.isSafeInteger(rolledPool) || rolledPool < 0) {
        throw new TypeError("HP pool must be a nonnegative browser-safe integer.");
      }
      if (!Array.isArray(candidates)) {
        throw new TypeError("HP pool candidates must be an array.");
      }
      const seen = new Set();
      const validated = candidates.map((candidate) => {
        if (!candidate || typeof candidate !== "object") {
          throw new TypeError("HP pool candidate must be an object.");
        }
        const id = candidate.combatantId;
        if (typeof id !== "string" || !id.trim() || seen.has(id)) {
          throw new TypeError("HP pool candidate IDs must be nonempty and unique.");
        }
        seen.add(id);
        if (!Number.isSafeInteger(candidate.currentHp) || candidate.currentHp < 0) {
          throw new TypeError("HP pool candidate HP must be a nonnegative integer.");
        }
        if (candidate.eligible !== undefined && typeof candidate.eligible !== "boolean") {
          throw new TypeError("HP pool candidate eligibility must be boolean.");
        }
        return { combatantId: id, currentHp: candidate.currentHp,
          eligible: candidate.eligible !== false };
      });
      let remaining = rolledPool;
      const affected = [];
      // JS stable sort preserves caller's selected tie order, like the Python oracle.
      validated.sort((a, b) => a.currentHp - b.currentHp);
      for (const candidate of validated) {
        if (!candidate.eligible || candidate.currentHp === 0) continue;
        if (candidate.currentHp > remaining) break;
        remaining -= candidate.currentHp;
        affected.push(candidate.combatantId);
      }
      return { affected, remaining };
    } catch (error) {
      console.error("Universal browser HP-pool allocation failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_HIT_POINT_POOL = Object.freeze({ allocateHitPointPool });
})();
