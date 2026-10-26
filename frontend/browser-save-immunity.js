(() => {
  "use strict";

  function sharedImmunityId(key) {
    try {
      const normalized = String(key || "").trim().toLowerCase();
      if (!normalized) throw new Error("Shared immunity key must be nonblank.");
      return `shared-save-immunity:${normalized}`;
    } catch (error) {
      console.error("Failed to normalize browser shared save-immunity key", {
        key, error,
      });
      throw error;
    }
  }

  function hasSharedImmunity(state, keys) {
    try {
      const wanted = new Set((keys || []).map(sharedImmunityId));
      return (state.timed_effects || []).some(
        (effect) => wanted.has(effect.effect_id),
      );
    } catch (error) {
      console.error("Failed browser shared save-immunity lookup", { keys, error });
      throw error;
    }
  }

  function grantSharedImmunities(state, keys, sourceId, round, options = {}) {
    try {
      const timed = window.IRON_PIT_BROWSER_TIMED;
      if (!timed) {
        throw new Error(
          "Shared save immunity requires browser-timed-conditions.js.",
        );
      }
      const applied = [];
      for (const key of (keys || [])) {
        const id = sharedImmunityId(key);
        if ((state.timed_effects || []).some(
          (effect) => effect.effect_id === id,
        )) {
          applied.push(id);
          continue;
        }
        const result = timed.apply(state, id, sourceId, {
          sourceEffectId: "shared-save-immunity",
          sourceTemplate: options.sourceTemplate || null,
          sourceIsMagical: Boolean(options.sourceIsMagical),
          appliedRound: round,
          expiresRound: null,
          expiryTiming: null,
          expiresAtStartOfSourceTurn: false,
          useDefaultPoisonRecovery: false,
        });
        if (result) applied.push(result);
      }
      return applied;
    } catch (error) {
      console.error("Failed browser shared save-immunity grant", {
        keys, sourceId, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_IMMUNITY = {
    sharedImmunityId, hasSharedImmunity, grantSharedImmunities,
  };
})();
