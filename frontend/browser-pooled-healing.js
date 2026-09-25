(() => {
  "use strict";

  const H = () => window.IRON_PIT_BROWSER_HEALING;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function capacity(target, numerator, denominator) {
    try {
      if (!Number.isInteger(numerator) || !Number.isInteger(denominator)
          || numerator <= 0 || denominator <= 0 || numerator > denominator) {
        throw new Error("Pooled-healing HP cap must be a positive fraction no greater than 1.");
      }
      const ceiling = Math.floor(S().effectiveMaxHp(target.state) * numerator / denominator);
      return Math.max(0, ceiling - target.state.current_hp);
    } catch (error) {
      console.error("Browser pooled-healing capacity failed", {
        target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  function resolve(targets, pool, numerator, denominator) {
    try {
      if (!Number.isInteger(pool) || pool <= 0) {
        throw new Error("Pooled healing requires a positive healing pool.");
      }
      if (!Array.isArray(targets) || !targets.length) {
        throw new Error("Pooled healing requires at least one target.");
      }

      let remaining = pool;
      const allocations = [];
      for (const target of targets) {
        if (remaining <= 0) break;
        const amount = Math.min(remaining, capacity(target, numerator, denominator));
        if (amount <= 0) continue;
        const healed = H().restore(target.state, amount);
        if (healed <= 0) continue;
        allocations.push({
          targetId: target.combatant_id,
          targetName: target.state.template.name,
          healed,
        });
        remaining -= healed;
      }
      return { allocations, remaining };
    } catch (error) {
      console.error("Browser pooled-healing resolution failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_POOLED_HEALING = { capacity, resolve };
})();
